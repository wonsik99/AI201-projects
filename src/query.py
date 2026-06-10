from __future__ import annotations

import os
import re
import sys

from dotenv import load_dotenv
from groq import Groq

from .config import MAX_DISTANCE_FOR_ANSWER
from .retrieve import RetrievalResult, retrieve


SYSTEM_PROMPT = """You are The Unofficial Guide for University of Michigan CS/EECS course selection.
Answer only from the retrieved source excerpts.
If the excerpts do not contain enough information to answer, say: "I don't have enough information in the collected documents to answer that."
Do not use outside knowledge.
Mention source titles naturally in the answer when they support a claim.
Keep the answer concise and practical for a student choosing CS/EECS courses."""


def _format_context(results: list[RetrievalResult]) -> str:
    blocks = []
    for index, item in enumerate(results, start=1):
        source = item.title or item.source_name
        blocks.append(
            f"[Source {index}: {source}; file={item.source_name}; chunk={item.chunk_index}; distance={item.distance:.3f}]\n{item.text}"
        )
    return "\n\n".join(blocks)


def _source_list(results: list[RetrievalResult]) -> list[str]:
    seen = set()
    sources = []
    for item in results:
        label = item.title or item.source_name
        if item.source_url:
            label = f"{label} ({item.source_url})"
        if label not in seen:
            sources.append(label)
            seen.add(label)
    return sources


def _extractive_answer(question: str, results: list[RetrievalResult]) -> tuple[str, list[str]]:
    generic_terms = {
        "what",
        "which",
        "course",
        "courses",
        "should",
        "take",
        "best",
        "want",
        "wants",
        "need",
        "needs",
        "does",
        "about",
        "before",
        "taking",
        "student",
        "students",
    }
    question_terms = {
        term.lower()
        for term in re.findall(r"[A-Za-z0-9]+", question)
        if len(term) > 2 and term.lower() not in generic_terms
    }
    sentences: list[tuple[int, str, str]] = []

    top_source = (results[0].title or results[0].source_name) if results else ""
    primary_results = [item for item in results if (item.title or item.source_name) == top_source]
    candidate_results = primary_results if primary_results else results[:3]

    for item in candidate_results:
        source = item.title or item.source_name
        for sentence in re.split(r"(?<=[.!?])\s+", item.text):
            clean = sentence.strip()
            if len(clean) < 40:
                continue
            sentence_terms = set(re.findall(r"[A-Za-z0-9]+", clean.lower()))
            score = len(question_terms & sentence_terms)
            if score:
                distance_penalty = int(item.distance * 10)
                sentences.append((score * 10 - distance_penalty, source, clean))

    if not sentences:
        for item in results[:2]:
            source = item.title or item.source_name
            first_sentence = re.split(r"(?<=[.!?])\s+", item.text.strip())[0]
            if first_sentence:
                sentences.append((0, source, first_sentence))

    selected = []
    used_sources = []
    seen = set()
    for _, source, sentence in sorted(sentences, key=lambda row: row[0], reverse=True):
        key = sentence.lower()
        if key in seen:
            continue
        selected.append(f"- {sentence} (source: {source})")
        if source not in used_sources:
            used_sources.append(source)
        seen.add(key)
        if len(selected) == 4:
            break

    answer = (
        "I found support for this in the collected documents. "
        "Since GROQ_API_KEY is not set, this is an extractive grounded answer from the retrieved chunks:\n"
        + "\n".join(selected)
    )
    return answer, used_sources


def ask(question: str) -> dict[str, object]:
    load_dotenv()
    results = retrieve(question)
    if not results or results[0].distance > MAX_DISTANCE_FOR_ANSWER:
        return {
            "answer": "I don't have enough information in the collected documents to answer that.",
            "sources": [],
            "retrieved_chunks": results,
        }

    context = _format_context(results)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        answer, used_source_titles = _extractive_answer(question, results)
        source_lookup = {
            item.title or item.source_name: item
            for item in results
        }
        sources = []
        for title in used_source_titles:
            item = source_lookup.get(title)
            if item is None:
                sources.append(title)
                continue
            label = item.title or item.source_name
            if item.source_url:
                label = f"{label} ({item.source_url})"
            sources.append(label)
        answer = answer.strip() + "\n\nSources:\n" + "\n".join(f"- {source}" for source in sources)
        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": results,
        }

    client = Groq(api_key=api_key)
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {question}\n\nRetrieved source excerpts:\n{context}",
            },
        ],
        temperature=0.1,
    )
    answer = response.choices[0].message.content or ""
    sources = _source_list(results)
    answer = answer.strip() + "\n\nSources:\n" + "\n".join(f"- {source}" for source in sources)
    return {"answer": answer, "sources": sources, "retrieved_chunks": results}


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit('Usage: python -m src.query "your question"')
    output = ask(question)
    print(output["answer"])
