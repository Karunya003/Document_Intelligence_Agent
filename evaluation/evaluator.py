from evaluation.metrics import (
    completeness_score,
    schema_validity,
    retrieval_coverage,
    confidence_score
)

REQUIRED_FIELDS = [
    "summary",
    "key_entities",
    "risks",
    "metrics"
]

def evaluate(output: dict, meta: dict) -> dict:
    return {
        "completeness": completeness_score(output, REQUIRED_FIELDS),
        "schema_validity": schema_validity(meta["schema_valid"]),
        "retrieval_coverage": retrieval_coverage(meta["chunks_used"]),
        "confidence": confidence_score(meta["confidence"])
    }