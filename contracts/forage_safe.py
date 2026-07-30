# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from dataclasses import dataclass
from genlayer import *


DISCLAIMER = (
    "Educational estimate only. NEVER eat a wild mushroom or plant based on "
    "this result. Always confirm with a qualified local expert."
)

RISK_LEVELS = {
    "LIKELY_HARMLESS": 0,
    "SAFE_LOOKALIKE_EXISTS": 1,
    "TOXIC": 2,
    "DEADLY_LOOKALIKE": 3,
    "UNKNOWN": 4,
}

# Taxa with lethal or severely toxic members that are classic foraging
# confusions. If any of these appear in the identification or in the
# look-alike list, the contract floors the risk regardless of what the model
# said. Genus-level entries are intentionally broad: for a caution engine an
# over-warning is acceptable, an under-warning is not.
DEADLY_TAXA = [
    # fungi
    "amanita", "galerina", "lepiota", "conocybe", "cortinarius", "gyromitra",
    "inocybe", "clitocybe", "omphalotus", "paxillus", "entoloma",
    "chlorophyllum", "russula subnigricans", "podostroma", "pleurocybella",
    "hypholoma", "scleroderma", "agaricus xanthodermus",
    # plants
    "conium", "cicuta", "aconitum", "atropa", "digitalis", "nerium",
    "ricinus", "taxus", "colchicum", "veratrum", "datura", "hyoscyamus",
    "abrus", "convallaria", "laburnum", "aethusa", "oenanthe", "gelsemium",
    "toxicodendron", "phytolacca", "solanum", "euphorbia", "narcissus",
    "heracleum", "delphinium", "rhododendron", "prunus laurocerasus",
]


@allow_storage
@dataclass
class Report:
    id: u256
    submitter: Address
    kind: str
    species_guess: str
    features: str
    habitat: str
    location: str
    verdict_json: str    # validated verdict (JSON string)
    evidence_json: str   # sources actually consulted (JSON string)
    grounded: bool       # True only if an authoritative source resolved
    disclaimer: str


class ForageSafe(gl.Contract):
    next_id: u256
    reports: TreeMap[u256, Report]

    def __init__(self):
        self.next_id = u256(0)

    # ------------------------------------------------------------------
    # Deterministic safety layer. Runs on every validator over the same
    # leader output, so it cannot diverge, and it is the part that actually
    # guarantees the consequential fields are sane before anything is stored.
    # ------------------------------------------------------------------
    def _harden(self, raw: str, grounded: bool) -> str:
        fallback = {
            "identified_species": "",
            "confirmed": False,
            "confidence": "low",
            "risk": "UNKNOWN",
            "toxic_lookalikes": [],
            "key_features_to_check": [],
            "reason": "The assessment could not be validated, so it is reported as unknown.",
            "sources_used": [],
        }

        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                data = dict(fallback)
        except Exception:
            data = dict(fallback)

        out = dict(fallback)
        for key in sorted(fallback.keys()):
            if key in data:
                out[key] = data[key]

        # --- normalise shapes -----------------------------------------
        species = str(out.get("identified_species") or "").strip()
        reason = str(out.get("reason") or "").strip() or fallback["reason"]

        lookalikes = out.get("toxic_lookalikes")
        if not isinstance(lookalikes, list):
            lookalikes = []
        lookalikes = [str(x).strip() for x in lookalikes if str(x).strip()]

        checks = out.get("key_features_to_check")
        if not isinstance(checks, list):
            checks = []
        checks = [str(x).strip() for x in checks if str(x).strip()]

        sources = out.get("sources_used")
        if not isinstance(sources, list):
            sources = []
        sources = [str(x).strip() for x in sources if str(x).strip()]

        confidence = str(out.get("confidence") or "low").strip().lower()
        if confidence not in ("low", "medium", "high"):
            confidence = "low"

        risk = str(out.get("risk") or "UNKNOWN").strip().upper()
        if risk not in RISK_LEVELS:
            risk = "UNKNOWN"

        confirmed = bool(out.get("confirmed")) if isinstance(out.get("confirmed"), bool) else False

        # --- guard 1: no authoritative grounding means no identification --
        # An ungrounded verdict is never allowed to assert a species or a
        # low risk, no matter how confident the model sounded.
        if not grounded or not sources:
            risk = "UNKNOWN"
            confirmed = False
            confidence = "low"
            reason = (
                "No authoritative source could be resolved for this specimen, so "
                "no identification is asserted. " + reason
            )

        # --- guard 2: known-deadly taxa floor the risk --------------------
        haystack = " ".join([species] + lookalikes).lower()
        hits = sorted({t for t in DEADLY_TAXA if t in haystack})
        if hits:
            if RISK_LEVELS[risk] < RISK_LEVELS["DEADLY_LOOKALIKE"] and risk != "UNKNOWN":
                risk = "DEADLY_LOOKALIKE"
            elif risk == "UNKNOWN":
                risk = "DEADLY_LOOKALIKE"
            confirmed = False
            reason = (
                "A taxon with lethal or severely toxic members is involved ("
                + ", ".join(hits)
                + "), so the risk is floored by the contract. " + reason
            )

        # --- guard 3: look-alikes contradict a harmless verdict -----------
        if lookalikes and risk == "LIKELY_HARMLESS":
            risk = "SAFE_LOOKALIKE_EXISTS"
            reason = (
                "Toxic look-alikes were listed, so a harmless verdict is not "
                "coherent and has been raised. " + reason
            )

        # --- guard 4: high confidence requires grounding and low risk -----
        if confidence == "high" and (risk in ("DEADLY_LOOKALIKE", "UNKNOWN") or not grounded):
            confidence = "medium" if grounded else "low"

        # --- guard 5: never allow an edibility claim to survive -----------
        lowered = reason.lower()
        for phrase in ("safe to eat", "edible", "you can eat", "fit for consumption"):
            if phrase in lowered:
                reason = (
                    "An edibility claim was removed by the contract. "
                    "ForageSafe never clears a specimen for consumption. " + reason
                )
                break

        if not checks:
            checks = [
                "Photograph the whole organism including the base in the ground",
                "Record habitat, substrate and nearby trees",
                "Have the specimen examined in hand by a qualified local expert",
            ]

        final = {
            "identified_species": species,
            "confirmed": confirmed,
            "confidence": confidence,
            "risk": risk,
            "toxic_lookalikes": lookalikes,
            "key_features_to_check": checks,
            "reason": reason,
            "sources_used": sources,
        }
        return json.dumps(final, sort_keys=True)

    @gl.public.write
    def identify(
        self,
        kind: str,
        species_guess: str,
        features: str,
        habitat: str,
        location: str,
    ) -> None:
        if kind not in ("mushroom", "plant"):
            raise Exception("kind must be 'mushroom' or 'plant'")
        if len(features.strip()) < 12:
            raise Exception("a substantive description of the specimen is required")

        # --------------------------------------------------------------
        # Non-deterministic block: derive candidates from the OBSERVED
        # FEATURES (the user's guess is only an untrusted hypothesis),
        # then ground every candidate in independent authoritative sources
        # before any verdict is formed.
        # --------------------------------------------------------------
        def investigate() -> str:
            # -- stage 1: candidate hypotheses from the features ---------
            candidate_prompt = (
                "A forager describes a wild " + kind + ".\n"
                "FEATURES: " + features + "\n"
                "HABITAT: " + habitat + "\n"
                "REGION: " + location + "\n"
                "UNVERIFIED USER GUESS (may be wrong, do not trust it): " + species_guess + "\n\n"
                "From the FEATURES alone, list the most likely species AND the most "
                "dangerous species that these features could not yet rule out. "
                "Return ONLY a JSON array of 2 to 4 binomial latin names, most "
                "likely first. No other text."
            )
            names = []
            try:
                rawc = gl.nondet.exec_prompt(candidate_prompt)
                rawc = rawc.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(rawc)
                if isinstance(parsed, list):
                    names = [str(n).strip() for n in parsed if str(n).strip()][:3]
            except Exception:
                names = []

            guess = species_guess.strip()
            if guess and guess.lower() not in [n.lower() for n in names]:
                names.append(guess)
            names = names[:3]

            # -- stage 2: independent authoritative grounding ------------
            evidence = []
            for name in names:
                slug = name.replace(" ", "%20")
                taxon = None
                # GBIF: authoritative taxonomic backbone. Also tells us
                # whether the name is a real accepted taxon at all.
                try:
                    r = gl.nondet.web.get(
                        "https://api.gbif.org/v1/species/match?name=" + slug
                    )
                    g = json.loads(r.body.decode("utf-8", errors="ignore"))
                    if isinstance(g, dict) and g.get("matchType") not in (None, "NONE"):
                        taxon = {
                            "source": "GBIF",
                            "query": name,
                            "scientificName": str(g.get("scientificName") or ""),
                            "rank": str(g.get("rank") or ""),
                            "status": str(g.get("status") or ""),
                            "family": str(g.get("family") or ""),
                            "genus": str(g.get("genus") or ""),
                            "matchType": str(g.get("matchType") or ""),
                        }
                except Exception:
                    taxon = None

                summary = ""
                # Wikipedia REST summary: short, stable, independent of the
                # taxonomic backbone above.
                try:
                    w = gl.nondet.web.get(
                        "https://en.wikipedia.org/api/rest_v1/page/summary/"
                        + name.replace(" ", "_")
                    )
                    wj = json.loads(w.body.decode("utf-8", errors="ignore"))
                    if isinstance(wj, dict):
                        summary = str(wj.get("extract") or "")[:900]
                except Exception:
                    summary = ""

                if taxon or summary:
                    evidence.append(
                        {"name": name, "taxon": taxon, "summary": summary}
                    )

            if not evidence:
                return json.dumps(
                    {
                        "grounded": False,
                        "evidence": [],
                        "verdict": {
                            "identified_species": "",
                            "confirmed": False,
                            "confidence": "low",
                            "risk": "UNKNOWN",
                            "toxic_lookalikes": [],
                            "key_features_to_check": [],
                            "reason": "No authoritative source resolved for any candidate.",
                            "sources_used": [],
                        },
                    },
                    sort_keys=True,
                )

            # -- stage 3: verdict grounded strictly in that evidence -----
            verdict_prompt = (
                "You are a cautious foraging safety analyst. Assess this " + kind + ".\n\n"
                "OBSERVED FEATURES: " + features + "\n"
                "HABITAT: " + habitat + "\n"
                "REGION: " + location + "\n\n"
                "AUTHORITATIVE EVIDENCE (GBIF taxonomy and Wikipedia summaries). "
                "Base your assessment ONLY on this evidence and the observed features. "
                "Do not use the user's guess as support for itself:\n"
                + json.dumps(evidence, sort_keys=True)[:6000] + "\n\n"
                "Return ONLY minified JSON with these keys:\n"
                '{"identified_species": string, "confirmed": bool, '
                '"confidence": "low"|"medium"|"high", '
                '"risk": "LIKELY_HARMLESS"|"SAFE_LOOKALIKE_EXISTS"|"TOXIC"|"DEADLY_LOOKALIKE"|"UNKNOWN", '
                '"toxic_lookalikes": [string], "key_features_to_check": [string], '
                '"reason": string, "sources_used": [string]}\n\n'
                "Rules:\n"
                "- sources_used must name the evidence entries you actually relied on.\n"
                "- If the evidence shows a lethal or severely toxic species that the "
                "observed features cannot rule out, risk is DEADLY_LOOKALIKE.\n"
                "- If the features do not discriminate between candidates, risk is UNKNOWN "
                "and confidence is low.\n"
                "- Never state or imply the specimen is safe to eat or edible.\n"
                "- List toxic look-alikes by binomial latin name."
            )
            rawv = gl.nondet.exec_prompt(verdict_prompt)
            rawv = rawv.replace("```json", "").replace("```", "").strip()
            try:
                verdict = json.loads(rawv)
            except Exception:
                verdict = {
                    "identified_species": "",
                    "confirmed": False,
                    "confidence": "low",
                    "risk": "UNKNOWN",
                    "toxic_lookalikes": [],
                    "key_features_to_check": [],
                    "reason": "The assessment could not be parsed.",
                    "sources_used": [],
                }

            return json.dumps(
                {"grounded": True, "evidence": evidence, "verdict": verdict},
                sort_keys=True,
            )

        # Validators check the SUBSTANCE of the leader's verdict against the
        # evidence it cites, not merely that it was worded cautiously.
        task = (
            "Investigate a foraging specimen: derive candidate species from the "
            "observed features, ground them in authoritative sources (GBIF taxonomy "
            "and Wikipedia), and return a safety verdict as JSON with the evidence used."
        )

        criteria = (
            "Judge the SUBSTANCE of the result, not its tone. Accept it only if ALL hold:\n"
            "1. The response is JSON containing 'grounded', 'evidence' and 'verdict'.\n"
            "2. Every species named in the verdict is taxonomically plausible and is "
            "supported by, or at least not contradicted by, the evidence entries included "
            "in the response.\n"
            "3. The toxicity classification is factually correct for the species named. "
            "Any species belonging to a genus with lethal or severely toxic members "
            "(for example Amanita, Galerina, Cortinarius, Lepiota, Gyromitra, Conium, "
            "Cicuta, Atropa, Nerium, Digitalis, Aconitum, Taxus, Convallaria) must be "
            "classified as TOXIC or DEADLY_LOOKALIKE, never LIKELY_HARMLESS.\n"
            "4. The risk level is not understated relative to the evidence. When the "
            "observed features cannot rule out a dangerous species, the risk must be "
            "DEADLY_LOOKALIKE or UNKNOWN rather than a lower level.\n"
            "5. Known toxic look-alikes for the named species are present in "
            "'toxic_lookalikes' when the evidence indicates they exist.\n"
            "6. The response never states or implies the specimen is safe to eat.\n"
            "Reject the result if it names a species the evidence contradicts, "
            "understates toxicity, or omits an obvious deadly look-alike."
        )

        raw = gl.eq_principle.prompt_non_comparative(
            investigate, task=task, criteria=criteria
        )

        # ---- deterministic validation before anything is stored --------
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        grounded = False
        evidence_json = "[]"
        verdict_raw = "{}"
        try:
            envelope = json.loads(cleaned)
            if isinstance(envelope, dict):
                grounded = bool(envelope.get("grounded")) is True
                ev = envelope.get("evidence")
                if isinstance(ev, list) and ev:
                    evidence_json = json.dumps(ev, sort_keys=True)
                else:
                    grounded = False
                verdict_raw = json.dumps(envelope.get("verdict"), sort_keys=True)
        except Exception:
            grounded = False

        verdict_json = self._harden(verdict_raw, grounded)

        rid = self.next_id
        self.reports[rid] = Report(
            id=rid,
            submitter=gl.message.sender_address,
            kind=kind,
            species_guess=species_guess,
            features=features,
            habitat=habitat,
            location=location,
            verdict_json=verdict_json,
            evidence_json=evidence_json,
            grounded=grounded,
            disclaimer=DISCLAIMER,
        )
        self.next_id = rid + u256(1)

    @gl.public.view
    def get_reports(self) -> dict:
        return {str(k): v for k, v in self.reports.items()}

    @gl.public.view
    def get_count(self) -> int:
        return self.next_id
