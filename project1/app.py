from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from src.query import ask


EXAMPLE_QUESTIONS = [
    "Which course should I take if I want full stack web development projects?",
    "EECS 388 security prerequisites EECS 281 EECS 370",
    "Who was the EECS 442 professor in 2025 winter term?",
    "Which course should I take for user interface design and usability testing?",
    "Where should I get pizza near campus?",
]


def _format_chunks(chunks) -> str:
    return "\n\n".join(
        [
            (
                f"{idx}. {chunk.title} | file={chunk.source_name} | "
                f"chunk {chunk.chunk_index} | distance={chunk.distance:.3f}\n"
                f"{chunk.text}"
            )
            for idx, chunk in enumerate(chunks, start=1)
        ]
    )


def handle_query(question: str):
    if not question.strip():
        return "", "", ""

    result = ask(question)
    sources = "\n".join(f"- {source}" for source in result["sources"])
    chunks = _format_chunks(result["retrieved_chunks"])
    return result["answer"], sources, chunks


def use_example(question: str) -> None:
    st.session_state.question = question
    st.session_state.run_query = True


def main() -> None:
    load_dotenv()
    st.set_page_config(page_title="UMich CS Unofficial Guide", page_icon="M", layout="wide")

    if "question" not in st.session_state:
        st.session_state.question = EXAMPLE_QUESTIONS[0]
    if "run_query" not in st.session_state:
        st.session_state.run_query = False

    st.title("UMich CS Unofficial Guide")
    st.caption(
        "Ask about collected UMich CS/EECS course pages, syllabi, prerequisites, "
        "projects, and instructor history."
    )
    if os.getenv("GROQ_API_KEY"):
        st.success("LLM mode: Groq API is connected.")
    else:
        st.warning("No GROQ_API_KEY found. The app is using a local extractive fallback for debugging.")

    with st.sidebar:
        st.header("Examples")
        st.caption("Click one to run it.")
        for index, example in enumerate(EXAMPLE_QUESTIONS, start=1):
            st.button(
                example,
                key=f"example_{index}",
                use_container_width=True,
                on_click=use_example,
                args=(example,),
            )
        st.divider()
        st.write("Outputs")
        st.write("- Grounded answer")
        st.write("- Sources used")
        st.write("- Retrieved chunks with distance scores")

    question = st.text_area(
        "Question",
        key="question",
        height=90,
        placeholder="Example: Which course should I take for full stack web development projects?",
    )

    submitted = st.button("Ask", type="primary")
    run_query = submitted or st.session_state.run_query
    if run_query:
        st.session_state.run_query = False
        if not question.strip():
            st.warning("Enter a question first.")
            return

        with st.spinner("Retrieving chunks and generating grounded answer..."):
            answer, sources, chunks = handle_query(question)

        st.subheader("Grounded Answer")
        st.write(answer)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Sources Used")
            if sources:
                st.markdown(sources)
            else:
                st.write("No sources used because the query was out of scope.")

        with col2:
            st.subheader("Retrieved Chunks")
            st.text_area("Top retrieved chunks", chunks, height=360, label_visibility="collapsed")


if __name__ == "__main__":
    main()
