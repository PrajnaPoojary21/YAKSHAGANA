"""
validator.py — Confidence-based validation for FAISS padya matches.

SCOPE (module 1 in the project spec — "is this specific FAISS candidate
reliable enough to display?"):

    This module runs AFTER matcher.find_top_k_matches() and decides
    ACCEPT / REJECT for the top-1 candidate. It does NOT decide whether
    the uploaded audio is Yakshagana at all, and it does NOT touch the
    transcript, Whisper, or story generation — that's module 2's job
    (transcription reliability / domain detection), which is a separate,
    larger piece of work described at the bottom of this file.

WHAT "SIMILARITY SCORE" ACTUALLY MEANS HERE:
    FAISS (via matcher.py's IndexFlatL2) returns an L2 (Euclidean)
    distance, not a similarity — smaller is better, and raw L2 numbers
    have no fixed 0..1 scale, so they must never be shown to users as
    a percentage. matcher.find_top_k_matches() already converts each
    candidate to a proper cosine similarity by loading the cached
    embeddings and computing dot(query, candidate) / (|query| * |candidate|)
    directly — see matcher.py's _cosine_similarity(). Everything in this
    file consumes that cosine_similarity field, not the raw distance.

PRECISION > RECALL:
    Per the spec, a wrong story is worse than asking the user to retry.
    MEDIUM-confidence matches are rejected, not shown with a caveat —
    there's no UI path in this module for "maybe".
"""

import re
import difflib

# ---------------------------------------------------------------------------
# Tunable weights / thresholds — INITIAL VALUES ONLY.
# These are reasonable starting points, not the output of a calibration run.
# See "HOW TO CALIBRATE THESE" at the bottom of this file before trusting
# them in production.
# ---------------------------------------------------------------------------

WEIGHTS = {
    "semantic": 0.55,       # cosine similarity between query & candidate embeddings
    "text": 0.15,           # character-level sequence similarity
    "token_overlap": 0.15,  # Jaccard overlap of Kannada word tokens
    "margin": 0.15,         # how clearly top-1 beats top-2 (ambiguity penalty)
}

MATCH_THRESHOLD = 0.75    # confidence >= this -> ACCEPT
REVIEW_THRESHOLD = 0.60   # confidence in [REVIEW_THRESHOLD, MATCH_THRESHOLD) -> "medium" (still rejected)
MIN_TRANSCRIPTION_WORDS = 3  # below this word count, confidence is scaled down hard


# ---------------------------------------------------------------------------
# Individual signals
# ---------------------------------------------------------------------------

def calculate_semantic_similarity(cosine_similarity):
    """Clip/rescale a cosine similarity (typically in [0,1] for same-language
    text on this model, but can dip slightly negative) into a clean [0,1]."""
    return max(0.0, min(1.0, cosine_similarity))


def _tokenize_kannada(text):
    if not text:
        return []
    # Kannada Unicode block: U+0C80–U+0CFF. Split on anything outside it.
    return [t for t in re.split(r'[^\u0C80-\u0CFF]+', text) if t]


def calculate_text_similarity(text1, text2):
    """Character-level sequence similarity (difflib ratio), 0..1.
    Catches near-duplicate strings that embedding similarity alone can
    under- or over-rate (e.g. two candidates that are semantically close
    but textually very different, or vice versa)."""
    if not text1 or not text2:
        return 0.0
    return difflib.SequenceMatcher(None, text1, text2).ratio()


def calculate_token_overlap(text1, text2):
    """Jaccard overlap of Kannada word tokens, 0..1."""
    t1 = set(_tokenize_kannada(text1))
    t2 = set(_tokenize_kannada(text2))
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / len(t1 | t2)


def calculate_top_k_margin(top1_similarity, top2_similarity):
    """
    Rewards a clear winner, penalizes ambiguity between the top two
    candidates:
        top1=0.91, top2=0.55 -> ~1.0 (confident, big gap)
        top1=0.72, top2=0.70 -> ~0.06 (ambiguous, near tie)
    A gap of 0.35+ is treated as "fully confident" (arbitrary starting
    point — recalibrate against real data, see bottom of file).
    """
    if top2_similarity is None:
        return 1.0  # only one candidate exists, no ambiguity signal available
    margin = top1_similarity - top2_similarity
    return max(0.0, min(1.0, margin / 0.35))


# ---------------------------------------------------------------------------
# Combined confidence + accept/reject decision
# ---------------------------------------------------------------------------

def calculate_match_confidence(transcription, top1, top2=None):
    """
    top1 / top2: dicts shaped like matcher.find_top_k_matches() entries,
    i.e. {"matched_padya": ..., "summary": ..., "distance": ..., "cosine_similarity": ...}

    Returns {"confidence": float in [0,1], "components": {...}} — components
    are for logging/debugging only, never shown to end users.
    """
    semantic = calculate_semantic_similarity(top1["cosine_similarity"])
    text_sim = calculate_text_similarity(transcription, top1["matched_padya"])
    token_sim = calculate_token_overlap(transcription, top1["matched_padya"])
    margin = calculate_top_k_margin(
        top1["cosine_similarity"],
        top2["cosine_similarity"] if top2 else None
    )

    confidence = (
        WEIGHTS["semantic"] * semantic +
        WEIGHTS["text"] * text_sim +
        WEIGHTS["token_overlap"] * token_sim +
        WEIGHTS["margin"] * margin
    )

    # Hard penalty for very short transcriptions — not enough signal to
    # trust any match, no matter how high the embedding similarity looks.
    word_count = len(transcription.split())
    if word_count < MIN_TRANSCRIPTION_WORDS:
        confidence *= word_count / MIN_TRANSCRIPTION_WORDS

    confidence = max(0.0, min(1.0, confidence))

    return {
        "confidence": confidence,
        "components": {
            "semantic_similarity": round(semantic, 4),
            "text_similarity": round(text_sim, 4),
            "token_overlap": round(token_sim, 4),
            "top_k_margin": round(margin, 4),
        },
    }


def validate_match(transcription, top_matches):
    """
    transcription : cleaned transcription text
    top_matches   : list from matcher.find_top_k_matches(text, top_k>=2)
                     (pass at least top_k=2 so margin scoring works)

    Returns a dict ready for the Flask layer to jsonify (minus the debug
    "_components" key, which app.py should strip before sending to the
    client — see the "Do not expose technical FAISS distances" rule):

        ACCEPT:
            {"success": True, "status": "matched", "confidence": 0.91,
             "padya": "...", "summary": "...", "message": None}

        REJECT:
            {"success": False, "status": "low_confidence" | "medium_confidence"
                                | "no_candidates" | "empty_transcription",
             "confidence": 0.42, "padya": None, "summary": None,
             "message": "..."}
    """
    if not transcription or not transcription.strip():
        return {
            "success": False, "status": "empty_transcription", "confidence": 0.0,
            "padya": None, "summary": None,
            "message": "ಆಡಿಯೊದಿಂದ ಪಠ್ಯ ಗುರುತಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
        }

    if not top_matches:
        return {
            "success": False, "status": "no_candidates", "confidence": 0.0,
            "padya": None, "summary": None,
            "message": "We could not confidently identify this padya from our reference collection.",
        }

    top1 = top_matches[0]
    top2 = top_matches[1] if len(top_matches) > 1 else None

    scored = calculate_match_confidence(transcription, top1, top2)
    confidence = scored["confidence"]

    if confidence >= MATCH_THRESHOLD:
        return {
            "success": True, "status": "matched", "confidence": round(confidence, 4),
            "padya": top1["matched_padya"], "summary": top1["summary"],
            "message": None,
            "_components": scored["components"],
        }

    # MEDIUM and LOW confidence both reject display — the spec is explicit
    # that "medium confidence" should not auto-show a possibly-wrong story.
    # The status field just lets logs/analytics tell "close" apart from
    # "way off"; the user-facing behavior is identical either way.
    status = "low_confidence" if confidence < REVIEW_THRESHOLD else "medium_confidence"
    return {
        "success": False, "status": status, "confidence": round(confidence, 4),
        "padya": None, "summary": None,
        "message": (
            "ಈ ಧ್ವನಿಮುದ್ರಣವನ್ನು ನಮ್ಮ ಸಂಗ್ರಹದ ಯಾವುದೇ ಪದ್ಯದೊಂದಿಗೆ ಖಚಿತವಾಗಿ "
            "ಹೊಂದಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಸ್ಪಷ್ಟ ಧ್ವನಿಮುದ್ರಣ ಅಥವಾ ಬೇರೆ ಪದ್ಯ "
            "ಪ್ರಯತ್ನಿಸಿ."
        ),
        "_components": scored["components"],
    }


# ---------------------------------------------------------------------------
# HOW TO CALIBRATE THESE THRESHOLDS (do this before trusting them):
#
# 1. Build a labeled set covering, per the spec:
#      positives — exact known padya, partial known padya, noisy known
#                  padya, known padya with transcription errors, different
#                  chunks of the same padya
#      negatives — unknown Yakshagana padya, a different Yakshagana padya,
#                  random Kannada sentence, Kannada movie dialogue, Kannada
#                  song, English/Hindi/Japanese sentence
# 2. For each example: run it through matcher.find_top_k_matches(), then
#    calculate_match_confidence(), and record the confidence + true label
#    (should-accept / should-reject).
# 3. Sweep MATCH_THRESHOLD over the recorded confidences and pick the value
#    that maximizes precision at an acceptable recall (remember: precision
#    matters more here). Plot confidence histograms for positives vs.
#    negatives — you want them well-separated, not just optimize one number.
# 4. Report accuracy / precision / recall / F1 / false-acceptance-rate /
#    false-rejection-rate at the chosen threshold, and re-check periodically
#    as the dataset grows past 6,872 entries.
#
# This file does not include that labeled set or sweep script — it needs
# real recordings/transcripts from your dataset, which weren't provided.
# ---------------------------------------------------------------------------