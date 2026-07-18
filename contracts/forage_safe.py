# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from dataclasses import dataclass
from genlayer import *


# Storage-friendly record of a single identification request + its AI verdict.
@allow_storage
@dataclass
class Report:
    id: u256
    submitter: Address
    kind: str            # "mushroom" | "plant"
    species_guess: str   # optional user guess (may be empty / wrong)
    features: str        # observed features (cap, gills, stem, spore print, ...)
    habitat: str
    location: str
    photo_ref: str       # IPFS hash or URL — kept for the record only
    verdict_json: str    # AI risk assessment as JSON (see _analyze)


class ForageSafe(gl.Contract):
    next_id: u256
    reports: TreeMap[u256, Report]

    def __init__(self):
        self.next_id = u256(0)

    # ---- core AI logic ---------------------------------------------------
    # `gather` (runs on the leader) fetches an optional web reference and
    # assembles the specimen context. The non-comparative equivalence principle
    # then has the leader produce the verdict while validators only check it
    # satisfies the safety criteria — this reaches consensus even for ambiguous
    # specimens, where forcing every validator to a byte-identical verdict fails.
    def _analyze(
        self,
        kind: str,
        species_guess: str,
        features: str,
        habitat: str,
        location: str,
    ) -> str:
        def gather() -> str:
            reference = ""
            guess = species_guess.strip()
            if guess:
                slug = guess.replace(" ", "_")
                url = "https://en.wikipedia.org/wiki/" + slug
                try:
                    page = gl.nondet.web.render(url, mode="text")
                    reference = page[:6000]
                except Exception:
                    reference = ""

            return (
                f"KIND: {kind}\n"
                f"CANDIDATE SPECIES (user guess, may be empty or wrong): {species_guess}\n"
                f"OBSERVED FEATURES: {features}\n"
                f"HABITAT: {habitat}\n"
                f"LOCATION: {location}\n"
                f"WEB REFERENCE (may be empty or unrelated, use only if relevant):\n"
                f"{reference}\n"
            )

        task = (
            f"You are ForageSafe, an EXTREMELY cautious wild {kind} safety assistant. "
            "Human safety is the only priority. Using the specimen data provided, "
            "return ONLY strict minified JSON, no markdown, with EXACTLY these keys: "
            '{"identified_species": string, "confirmed": boolean, '
            '"confidence": "low"|"medium"|"high", '
            '"risk": "DEADLY_LOOKALIKE"|"TOXIC"|"SAFE_LOOKALIKE_EXISTS"|"LIKELY_HARMLESS"|"UNKNOWN", '
            '"toxic_lookalikes": string[], "key_features_to_check": string[], "reason": string}. '
            "Rules: NEVER state or imply the specimen is safe to eat or edible. "
            "If the observed features cannot rule out a dangerous look-alike, set "
            "'risk' to UNKNOWN or the strongest applicable warning and 'confidence' to 'low'. "
            "Always list known deadly/toxic look-alikes for the candidate when they exist. "
            "Prefer caution over precision."
        )

        criteria = (
            "The response is strictly valid minified JSON containing exactly the keys "
            "identified_species, confirmed, confidence, risk, toxic_lookalikes, "
            "key_features_to_check and reason, with the correct value types. "
            "The 'risk' value is one of DEADLY_LOOKALIKE, TOXIC, SAFE_LOOKALIKE_EXISTS, "
            "LIKELY_HARMLESS or UNKNOWN. "
            "The response NEVER claims the specimen is safe to eat or edible. "
            "If a deadly or toxic look-alike is plausible, 'risk' is not LIKELY_HARMLESS."
        )

        result = gl.eq_principle.prompt_non_comparative(
            gather, task=task, criteria=criteria
        )
        result = result.replace("```json", "").replace("```", "").strip()
        # normalise; fall back to raw string if the model added stray text
        try:
            return json.dumps(json.loads(result), sort_keys=True)
        except Exception:
            return result

    # ---- public write ----------------------------------------------------
    @gl.public.write
    def identify(
        self,
        kind: str,
        species_guess: str,
        features: str,
        habitat: str,
        location: str,
        photo_ref: str,
    ) -> None:
        if kind not in ("mushroom", "plant"):
            raise Exception("kind must be 'mushroom' or 'plant'")
        if not features.strip():
            raise Exception("features are required")

        verdict = self._analyze(kind, species_guess, features, habitat, location)

        try:
            parsed = json.loads(verdict)
        except Exception:
            parsed = {
                "identified_species": species_guess,
                "confirmed": False,
                "confidence": "low",
                "risk": "UNKNOWN",
                "toxic_lookalikes": [],
                "key_features_to_check": [],
                "reason": "Analysis could not be parsed.",
            }

        # safety disclaimer is always attached, no matter what the model said
        parsed["disclaimer"] = (
            "Educational estimate only. NEVER eat a wild mushroom or plant based "
            "on this result. Always confirm with a qualified local expert."
        )

        rid = self.next_id
        self.reports[rid] = Report(
            id=rid,
            submitter=gl.message.sender_address,
            kind=kind,
            species_guess=species_guess,
            features=features,
            habitat=habitat,
            location=location,
            photo_ref=photo_ref,
            verdict_json=json.dumps(parsed, sort_keys=True),
        )
        self.next_id = rid + u256(1)

    # ---- public views ----------------------------------------------------
    @gl.public.view
    def get_reports(self) -> dict:
        return {str(k): v for k, v in self.reports.items()}

    @gl.public.view
    def get_count(self) -> int:
        return self.next_id
