# Project 1 Planning: The Unofficial Guide

## Domain

I chose University of Michigan CS/EECS course selection. My first idea was professor reviews, but the public review sites were hard to collect from in a reliable way, so I am focusing on course pages, syllabi, assignment pages, and faculty teaching pages that still help students decide what class fits them.

This is useful because the official course catalog is usually too short. It might say a course is "web systems" or "computer organization," but it does not quickly show what projects students build, what prerequisites matter, whether the class is project-heavy, or what kind of student the course is good for.

## Documents

I saved the sources as cleaned `.txt` files in `documents/`, grouped by EECS number. My source URLs are:

1. https://eecs203.github.io/eecs203.org/
2. https://ece.engin.umich.edu/academics/course-information/course-descriptions/eecs-203/
3. https://eecs280.org/
4. https://eecs280.org/syllabus.html
5. https://eecs281staff.github.io/eecs281.org/
6. https://eecs281staff.github.io/eecs281.org/syllabus.html
7. https://eecs285.org/assets/syllabus.html
8. https://eecs370.github.io/
9. https://eecs370.github.io/resources/projects_hws.html
10. https://eecs376.org/
11. https://eecs376.org/syllabus.html
12. https://eecs388.org/
13. https://eecs441soloway.github.io/
14. https://eecs441.eecs.umich.edu/
15. https://web.eecs.umich.edu/~stellayu/
16. https://eecs445-f16.github.io/
17. https://www.eecs.umich.edu/courses/eecs473/overview.html
18. https://eecs481.org/
19. https://eecs481.org/hw6.html
20. https://web.eecs.umich.edu/~harshavm/eecs482/
21. https://web.eecs.umich.edu/~harshavm/eecs482/syllabus.html
22. https://eecs485.org/
23. https://eecs485.org/syllabus.html
24. https://web.eecs.umich.edu/~sugih/courses/eecs489/
25. https://github.com/mosharaf/eecs489
26. https://web.eecs.umich.edu/~kuipers/teaching/eecs492-F10.html
27. https://laura-burdick.github.io/papers/SyllabusEECS492Winter2023.pdf
28. https://eecs493staff.github.io/eecs493.org/
29. https://www.eecs494.com/eecs_494_syllabus/eecs_494_syllabus.html

## Chunking Strategy

Chunk size: 750 characters

Overlap: about 150 characters

Reasoning: My documents are short cleaned notes, not long PDFs. I want each chunk to usually contain one complete course-selection idea, like "EECS 485 has five projects" or "EECS 388 requires EECS 281." I started with larger chunks, but after inspecting sample chunks I lowered the size to 750 and made the overlap paragraph/sentence-aware so chunks do not start in the middle of a word.

## Retrieval Approach

Embedding model: `sentence-transformers/all-MiniLM-L6-v2`

Top-k: 5

Production tradeoff reflection: For this class project I chose MiniLM because it is free and local. If this were a real student-facing tool, I would compare cost, latency, privacy, context length, and accuracy on course slang. I would also care about metadata filtering because if a student says "EECS 445," the system should strongly prefer EECS 445 chunks.

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which course should I take if I want full stack web development projects? | EECS 485, because it covers front end/back end and web projects. |
| 2 | EECS 388 security prerequisites EECS 281 EECS 370 | EECS 388 is the security course; EECS 281 is required and EECS 201/370 are recommended. |
| 3 | EECS 281 algorithms projects graph search priority queues hash tables | EECS 281 has algorithms projects involving graph search, priority queues, hash tables, and optimization. |
| 4 | Who was the EECS 442 professor in 2025 winter term? | Stella Yu was the professor/instructor for EECS 442 Computer Vision in Winter 2025. |
| 5 | What math background does EECS 445 warn students need? | EECS 445 warns students need linear algebra and probability background. |

## Anticipated Challenges

1. Some questions might sound like professor-review questions, but my source set mostly has course pages. If someone asks "which professor is nicest," the system should refuse or say the documents do not contain that.

2. Retrieval might confuse prerequisite questions across courses. For example, "what background do I need" could match EECS 388 prerequisites even if the user meant EECS 445. Course-number metadata filtering would help.

3. Cleaned notes are easier to retrieve than raw HTML, but they are less unofficial than Reddit or Rate My Professors. I need to be honest about that in the README.

## Architecture

My pipeline is basically:

documents folder -> clean text -> chunk text -> embed chunks -> store in ChromaDB -> retrieve top 5 chunks -> answer with sources -> show it in Streamlit

The main thing I need to remember is that the answer step should only use the retrieved chunks. If the chunks do not have the answer, the app should say it does not know instead of guessing.

## AI Tool Plan

Milestone 3 - Ingestion and chunking: I will ask Codex to write the document loader and chunker using my chunk size and overlap. I will check the printed sample chunks myself and change the code if chunks are cut off or hard to read.

Milestone 4 - Embedding and retrieval: I will ask Codex to connect `all-MiniLM-L6-v2` to ChromaDB and return top-k chunks with source metadata. I will test retrieval before adding generation because bad retrieval would make the answer bad no matter what model I use.

Milestone 5 - Generation and interface: I will ask Codex to make the answer use only retrieved chunks and show sources. I will also ask it to make a simple Streamlit interface with question input, answer output, source output, and retrieved chunk output.
