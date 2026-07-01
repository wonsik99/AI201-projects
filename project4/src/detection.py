import json
import os
import re
import statistics

from dotenv import load_dotenv
from groq import Groq

from labels import map_confidence

load_dotenv()

TRANSITION_PHRASES = (
    "furthermore",
    "in conclusion",
    "it is important to note",
    "additionally",
    "moreover",
    "in summary",
    "on the other hand",
)

LLM_PROMPT = (
    "Assess whether the following text reads as human-written or AI-generated. "
    "Return ONLY valid JSON with one key:\n"
    '{"ai_likelihood": 0.0}\n'
    "Use a float from 0.0 (very likely human-written) to 1.0 (very likely "
    "AI-generated)."
)


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"[.!?]+", text)
    return [part.strip() for part in parts if part.strip()]


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def heuristic_score(text: str) -> float:
    sentences = split_sentences(text)
    words = tokenize_words(text)
    sentence_count = max(len(sentences), 1)
    word_count = max(len(words), 1)

    lengths = [len(sentence) for sentence in sentences] or [len(text)]
    mean_length = statistics.mean(lengths)
    if mean_length == 0 or len(lengths) < 2:
        cv = 0.0
    else:
        cv = statistics.pstdev(lengths) / mean_length

    unique_words = set(words)
    ttr = len(unique_words) / word_count

    lowered = text.lower()
    transition_count = sum(lowered.count(phrase) for phrase in TRANSITION_PHRASES)

    cv_subscore = clamp(1.0 - (cv / 0.45))
    ttr_subscore = clamp(1.0 - (ttr / 0.55))
    transition_subscore = clamp(transition_count / sentence_count / 0.35)

    return round(
        0.45 * cv_subscore + 0.35 * ttr_subscore + 0.20 * transition_subscore,
        4,
    )


def llm_score(text: str, client: Groq | None = None) -> float:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return 0.5

    groq_client = client or Groq(api_key=api_key)
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": LLM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=40,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()
        payload = json.loads(raw)
        return round(clamp(float(payload["ai_likelihood"])), 4)
    except Exception:
        return 0.5


def combine_scores(llm: float, heuristic: float, sentence_count: int) -> float:
    if sentence_count < 2:
        confidence = 0.85 * llm + 0.15 * heuristic
    else:
        confidence = 0.65 * llm + 0.35 * heuristic

    if abs(llm - heuristic) > 0.35:
        confidence = 0.5 * confidence + 0.25

    return round(clamp(confidence), 4)


def analyze_text(text: str, client: Groq | None = None) -> dict:
    llm = llm_score(text, client=client)
    heuristic = heuristic_score(text)
    sentence_count = len(split_sentences(text))
    confidence = combine_scores(llm, heuristic, sentence_count)
    attribution, label = map_confidence(confidence)

    return {
        "attribution": attribution,
        "confidence": confidence,
        "label": label,
        "llm_score": llm,
        "heuristic_score": heuristic,
    }
