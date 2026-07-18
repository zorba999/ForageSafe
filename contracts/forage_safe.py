# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from dataclasses import dataclass
from genlayer import *


# Constant safety disclaimer, always stored on-chain with every report.
DISCLAIMER = (
    "Educational estimate only. NEVER eat a wild mushroom or plant based on "
    "this result. Always confirm with a qualified local expert."
)


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
    verdict_json: str    # raw AI risk assessment (JSON string, parsed by the UI)
    disclaimer: str      # constant safety notice


class ForageSafe(gl.Contract):
    next_id: u256
    reports: TreeMap[u256, Report]

    def __init__(self):
        self.next_id = u256(0)

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

        # --- non-deterministic block (runs on the leader) ---------------
        # Fetch an optional web reference (fast HTTP, fully failure-safe),
        # then let the LLM produce a safety-first verdict. Validators only
        # check the leader's output satisfies lenient safety criteria, which
        # keeps consensus fast and reliable.
        def gather() -> str:
            reference = ""
            guess = species_guess.strip()
            if guess:
                slug = guess.replace(" ", "_")
                try:
                    resp = gl.nondet.web.get("https://en.wikipedia.org/wiki/" + slug)
                    reference = resp.body.decode("utf-8", errors="ignore")[:3000]
                except Exception:
                    reference = ""

            return (
                f"KIND: {kind}\n"
                f"SPECIES GUESS (may be empty/wrong): {species_guess}\n"
                f"FEATURES: {features}\n"
                f"HABITAT: {habitat}\n"
                f"LOCATION: {location}\n"
                f"WEB REFERENCE (optional):\n{reference}\n"
            )

        task = (
            "You are a very cautious wild mushroom/plant safety assistant. "
            "Human safety is the only priority. From the specimen data, output "
            "ONLY a minified JSON object with these keys: identified_species "
            "(string), confirmed (bool), confidence ('low'|'medium'|'high'), "
            "risk ('DEADLY_LOOKALIKE'|'TOXIC'|'SAFE_LOOKALIKE_EXISTS'|"
            "'LIKELY_HARMLESS'|'UNKNOWN'), toxic_lookalikes (string array), "
            "key_features_to_check (string array), reason (string). "
            "Never say it is safe to eat. If a dangerous look-alike cannot be "
            "ruled out, use UNKNOWN or a warning risk and low confidence. "
            "Output JSON only, no markdown."
        )

        criteria = (
            "The response is a JSON object assessing a foraging specimen. "
            "It contains a 'risk' field and a 'reason'. "
            "It never claims the specimen is safe or edible to eat."
        )

        verdict = gl.eq_principle.prompt_non_comparative(
            gather, task=task, criteria=criteria
        )

        # --- deterministic storage (trivial: no parsing => no divergence) ---
        clean = verdict.replace("```json", "").replace("```", "").strip()

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
            verdict_json=clean,
            disclaimer=DISCLAIMER,
        )
        self.next_id = rid + u256(1)

    # ---- public views ----------------------------------------------------
    @gl.public.view
    def get_reports(self) -> dict:
        return {str(k): v for k, v in self.reports.items()}

    @gl.public.view
    def get_count(self) -> int:
        return self.next_id
