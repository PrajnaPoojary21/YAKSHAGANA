"""
test_validator.py — unit tests for the parts of validator.py that don't
need FAISS/the embedding model (those need matcher.find_top_k_matches(),
which needs the real dataset + SentenceTransformer, and can't run in this
sandbox). This covers the pure scoring functions with hand-built inputs
that mimic what matcher.py would hand validate_match().

Run with: python -m pytest test_validator.py -v
    (or just: python test_validator.py)
"""

from validator import (
    calculate_text_similarity,
    calculate_token_overlap,
    calculate_top_k_margin,
    calculate_match_confidence,
    validate_match,
    MATCH_THRESHOLD,
)

PADYA_KRISHNA = "ಶ್ರೀಕೃಷ್ಣ ಗೋಪಿಕೆಯರೊಡನೆ ಆಡುತ ಬಂದನು ಯಮುನಾ ತೀರದಿ"
PADYA_RAMA = "ಶ್ರೀರಾಮ ಲಕ್ಷ್ಮಣ ಸೀತೆಯರೊಡನೆ ಪಯಣಿಸಿದನು ವನವಾಸಕೆ"


def make_candidate(text, summary, cosine_similarity, distance=0.0):
    return {
        "matched_padya": text,
        "summary": summary,
        "distance": distance,
        "cosine_similarity": cosine_similarity,
    }


def test_exact_match_high_confidence():
    top1 = make_candidate(PADYA_KRISHNA, "summary A", cosine_similarity=0.97)
    top2 = make_candidate(PADYA_RAMA, "summary B", cosine_similarity=0.40)
    result = calculate_match_confidence(PADYA_KRISHNA, top1, top2)
    assert result["confidence"] >= MATCH_THRESHOLD, result


def test_ambiguous_top1_top2_lowers_confidence():
    close_top1 = make_candidate(PADYA_KRISHNA, "s", cosine_similarity=0.72)
    close_top2 = make_candidate(PADYA_RAMA, "s", cosine_similarity=0.70)
    clear_top1 = make_candidate(PADYA_KRISHNA, "s", cosine_similarity=0.91)
    clear_top2 = make_candidate(PADYA_RAMA, "s", cosine_similarity=0.55)

    ambiguous = calculate_match_confidence(PADYA_KRISHNA, close_top1, close_top2)
    clear = calculate_match_confidence(PADYA_KRISHNA, clear_top1, clear_top2)
    assert ambiguous["confidence"] < clear["confidence"]


def test_unknown_padya_rejected_despite_nearest_neighbour():
    # Simulates the spec's core scenario: audio is an out-of-dataset Rama
    # padya, FAISS's nearest available candidate is an unrelated Krishna
    # padya. Similarity should be too low/text-mismatched to accept.
    transcription = "ಶ್ರೀರಾಮ ಹನುಮಂತ ಸೀತಾ ಲಂಕಾ ರಾವಣ ವಿಷಯದ ಪದ್ಯ ಇದು"
    weak_candidate = make_candidate(PADYA_KRISHNA, "krishna story", cosine_similarity=0.58)
    result = validate_match(transcription, [weak_candidate])
    assert result["success"] is False
    assert result["padya"] is None


def test_empty_transcription_rejected():
    result = validate_match("", [make_candidate(PADYA_KRISHNA, "s", 0.99)])
    assert result["status"] == "empty_transcription"


def test_no_candidates_rejected():
    result = validate_match("ಏನೋ ಪಠ್ಯ", [])
    assert result["status"] == "no_candidates"


def test_very_short_transcription_penalized():
    top1 = make_candidate(PADYA_KRISHNA, "s", cosine_similarity=0.95)
    long_conf = calculate_match_confidence("ಶ್ರೀಕೃಷ್ಣ ಗೋಪಿಕೆಯರೊಡನೆ ಆಡುತ ಬಂದನು", top1)
    short_conf = calculate_match_confidence("ಕೃಷ್ಣ", top1)
    assert short_conf["confidence"] < long_conf["confidence"]


def test_identical_text_has_high_text_and_token_similarity():
    assert calculate_text_similarity(PADYA_KRISHNA, PADYA_KRISHNA) == 1.0
    assert calculate_token_overlap(PADYA_KRISHNA, PADYA_KRISHNA) == 1.0


def test_margin_no_second_candidate_is_neutral():
    assert calculate_top_k_margin(0.9, None) == 1.0


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {t.__name__} -> {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")