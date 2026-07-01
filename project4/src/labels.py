LABEL_LIKELY_AI = (
    "Likely AI-generated (high confidence). Our analysis found strong signals "
    "associated with generated writing. If you wrote this yourself, you can "
    "appeal this result."
)

LABEL_LIKELY_HUMAN = (
    "Likely human-written (high confidence). We did not find strong "
    "AI-generation signals in this submission."
)

LABEL_UNCERTAIN = (
    "Origin uncertain. Our checks found mixed signals, so we are not making a "
    "strong attribution claim. You can still appeal if you want a human review."
)

HUMAN_THRESHOLD = 0.30
AI_THRESHOLD = 0.75


def map_confidence(confidence: float) -> tuple[str, str]:
    if confidence <= HUMAN_THRESHOLD:
        return "likely_human", LABEL_LIKELY_HUMAN
    if confidence >= AI_THRESHOLD:
        return "likely_ai", LABEL_LIKELY_AI
    return "uncertain", LABEL_UNCERTAIN
