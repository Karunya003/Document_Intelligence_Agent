from typing import Dict, List

def completeness_score(output: Dict, required_fields: List[str]) -> float:
    present = sum(1 for f in required_fields if output.get(f))
    return present / len(required_fields)


def schema_validity(is_valid: bool) -> float:
    return 1.0 if is_valid else 0.0


def retrieval_coverage(num_chunks_used: int, min_chunks: int = 3) -> float:
    return min(num_chunks_used / min_chunks, 1.0)


def confidence_score(model_confidence: float) -> float:
    return model_confidence