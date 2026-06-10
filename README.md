# The Unofficial Guide - Project 1

This project is a small RAG system for choosing University of Michigan CS/EECS courses. A student can ask a question like "Which course should I take for web development?" and the system retrieves relevant source chunks before producing a grounded answer with source attribution.

## Domain

My domain is UMich CS/EECS course selection. I originally wanted to focus only on professor reviews, but Rate My Professors was not reliable to collect from automatically. I narrowed the system to public student-facing course materials: course homepages, syllabi, assignment pages, faculty teaching pages, and public r/uofm discussion threads. This is useful because official course catalog descriptions are short, while course sites and student discussions show what students actually have to do: projects, exams, prerequisites, tools, staff, instructor history, workload, and course structure.

## Document Sources

I collected 48 source documents as cleaned `.txt` notes under `documents/`, organized by EECS course number.

| # | Source | Type | URL or file path |
|---|--------|------|------------------|
| 1 | EECS 203 overview | Public course website and ECE course description | `documents/eecs203/01_overview.txt`, https://eecs203.github.io/eecs203.org/ ; https://ece.engin.umich.edu/academics/course-information/course-descriptions/eecs-203/ |
| 2 | EECS 280 course homepage | Public course website | `documents/eecs280/01_main.txt`, https://eecs280.org/ |
| 3 | EECS 280 syllabus | Public course syllabus | `documents/eecs280/02_syllabus.txt`, https://eecs280.org/syllabus.html |
| 4 | EECS 281 course homepage | Public course website | `documents/eecs281/01_main.txt`, https://eecs281staff.github.io/eecs281.org/ |
| 5 | EECS 281 syllabus | Public course syllabus | `documents/eecs281/02_syllabus.txt`, https://eecs281staff.github.io/eecs281.org/syllabus.html |
| 6 | EECS 285 syllabus | Public course syllabus | `documents/eecs285/01_syllabus.txt`, https://eecs285.org/assets/syllabus.html |
| 7 | EECS 370 course homepage | Public course website | `documents/eecs370/01_main.txt`, https://eecs370.github.io/ |
| 8 | EECS 370 assignments page | Public assignments page | `documents/eecs370/02_assignments.txt`, https://eecs370.github.io/resources/projects_hws.html |
| 9 | EECS 376 overview and syllabus | Public course website and syllabus | `documents/eecs376/01_overview_syllabus.txt`, https://eecs376.org/ ; https://eecs376.org/syllabus.html |
| 10 | EECS 388 overview | Public course website | `documents/eecs388/01_overview.txt`, https://eecs388.org/ |
| 11 | EECS 441 mobile app development | Public course websites | `documents/eecs441/01_mobile_app_development.txt`, https://eecs441soloway.github.io/ ; https://eecs441.eecs.umich.edu/ |
| 12 | EECS 442 Winter 2025 instructor source | Public faculty teaching page | `documents/eecs442/01_w25_stella_yu.txt`, https://web.eecs.umich.edu/~stellayu/ |
| 13 | EECS 445 syllabus | Public course syllabus | `documents/eecs445/01_syllabus.txt`, https://eecs445-f16.github.io/ |
| 14 | EECS 473 embedded systems overview | Public course overview | `documents/eecs473/01_embedded_systems.txt`, https://www.eecs.umich.edu/courses/eecs473/overview.html |
| 15 | EECS 481 software engineering overview and homework | Public course website and homework page | `documents/eecs481/01_overview_and_hw.txt`, https://eecs481.org/ ; https://eecs481.org/hw6.html |
| 16 | EECS 482 operating systems | Public course website and syllabus | `documents/eecs482/01_operating_systems.txt`, https://web.eecs.umich.edu/~harshavm/eecs482/ ; https://web.eecs.umich.edu/~harshavm/eecs482/syllabus.html |
| 17 | EECS 485 course homepage | Public course website | `documents/eecs485/01_main.txt`, https://eecs485.org/ |
| 18 | EECS 485 syllabus | Public course syllabus | `documents/eecs485/02_syllabus.txt`, https://eecs485.org/syllabus.html |
| 19 | EECS 489 computer networks | Public course website and public repository | `documents/eecs489/01_computer_networks.txt`, https://web.eecs.umich.edu/~sugih/courses/eecs489/ ; https://github.com/mosharaf/eecs489 |
| 20 | EECS 492 introduction to AI | Public course page and public syllabus PDF | `documents/eecs492/01_intro_ai.txt`, https://web.eecs.umich.edu/~kuipers/teaching/eecs492-F10.html ; https://laura-burdick.github.io/papers/SyllabusEECS492Winter2023.pdf |
| 21 | EECS 493 user interface development | Public course website | `documents/eecs493/01_user_interface_dev.txt`, https://eecs493staff.github.io/eecs493.org/ |
| 22 | EECS 494 game design | Public course syllabus | `documents/eecs494/01_game_design.txt`, https://www.eecs494.com/eecs_494_syllabus/eecs_494_syllabus.html |
| 23 | EECS 281 workload discussion | Reddit r/uofm thread | `documents/eecs281/03_reddit_workload.txt`, https://www.reddit.com/r/uofm/comments/1q9d894/eecs_281_workload_questions/ |
| 24 | EECS 370 and 485 workload discussion | Reddit r/uofm threads | `documents/eecs370/03_reddit_370_485_workload.txt`, https://www.reddit.com/r/uofm/comments/rwpiyv/eecs_workload_check/ ; https://www.reddit.com/r/uofm/comments/162bmcv/words_of_wisdomadvice_on_eecs_370_485_and_how_to/ |
| 25 | EECS 370 and 376 schedule discussion | Reddit r/uofm thread | `documents/eecs376/02_reddit_370_376_combo.txt`, https://www.reddit.com/r/uofm/comments/uzdwqh/how_doable_is_eecs_370_and_eecs_376_for_fall/ |
| 26 | EECS 482 course decision discussion | Reddit r/uofm thread | `documents/eecs482/02_reddit_should_take.txt`, https://www.reddit.com/r/uofm/comments/1mbzdyk/should_i_take_eecs_482/ |
| 27 | EECS 485 student recommendation discussion | Reddit r/uofm thread | `documents/eecs485/03_reddit_recommendation.txt`, https://www.reddit.com/r/uofm/comments/1hkyd62/eecs_485_web_systems_course_recommendationhonest/ |
| 28 | EECS 203 and 280 preparation discussion | Reddit r/uofm thread | `documents/eecs203/02_reddit_203_280_prep.txt`, https://www.reddit.com/r/uofm/comments/nxnp7k/preparing_for_eecs_203_and_eecs_280/ |
| 29 | EECS 203, EECS 280, and Calc 2 schedule discussion | Reddit r/uofm thread | `documents/eecs203/03_reddit_203_280_calc_schedule.txt`, https://www.reddit.com/r/uofm/comments/17pgslq/eecs_280_calc_2_eecs_203_at_the_same_time/ |
| 30 | EECS 280 rigor discussion | Reddit r/uofm thread | `documents/eecs280/03_reddit_rigor.txt`, https://www.reddit.com/r/uofm/comments/151lctq/eecs_280_rigor/ |
| 31 | EECS 280 workload and tools discussion | Reddit r/uofm thread | `documents/eecs280/04_reddit_workload_tools.txt`, https://www.reddit.com/r/uofm/comments/6ycvju/eecs_280_workload/ |
| 32 | EECS 280 project ranking discussion | Reddit r/uofm thread | `documents/eecs280/05_reddit_project_ranking.txt`, https://www.reddit.com/r/uofm/comments/nayizd/how_are_the_eecs_280_projects_ranked/ |
| 33 | EECS 281 informal survival guide | Reddit r/uofm thread | `documents/eecs281/04_reddit_lazy_guide.txt`, https://www.reddit.com/r/uofm/comments/1dc4yi0/the_lazy_students_guide_to_eecs_281/ |
| 34 | EECS 280 versus EECS 281 project/autograder discussion | Reddit r/uofm thread | `documents/eecs281/05_reddit_281_vs_280_autograder.txt`, https://www.reddit.com/r/uofm/comments/a1edc6/eecs_280_vs_eecs_281_projectsautograder/ |
| 35 | EECS 281 difficulty discussion | Reddit r/uofm thread | `documents/eecs281/06_reddit_how_bad_281.txt`, https://www.reddit.com/r/uofm/comments/l6nx27/how_bad_is_eecs_281/ |
| 36 | EECS 270 versus EECS 370 workload discussion | Reddit r/uofm thread | `documents/eecs370/04_reddit_270_vs_370_workload.txt`, https://www.reddit.com/r/uofm/comments/rru85c/eecs_270_vs_370_workload/ |
| 37 | EECS 370 class pairing discussion | Reddit r/uofm thread | `documents/eecs370/05_reddit_class_to_take_with_370.txt`, https://www.reddit.com/r/uofm/comments/4gm8wf/what_class_to_take_with_eecs_370/ |
| 38 | EECS 376 class pairing discussion | Reddit r/uofm thread | `documents/eecs376/03_reddit_classes_to_take_with_376.txt`, https://www.reddit.com/r/uofm/comments/1ki1vy8/classes_to_take_with_eecs_376/ |
| 39 | EECS 376 difficulty discussion | Reddit r/uofm thread | `documents/eecs376/04_reddit_376_sad.txt`, https://www.reddit.com/r/uofm/comments/lcsvga/eecs_376_sad/ |
| 40 | EECS 376 learning resources discussion | Reddit r/uofm thread | `documents/eecs376/05_reddit_learning_376.txt`, https://www.reddit.com/r/uofm/comments/1gy7ih1/eecs_376_students_how_are_you_learning_the/ |
| 41 | EECS 388 general thoughts discussion | Reddit r/uofm thread | `documents/eecs388/02_reddit_thoughts_388.txt`, https://www.reddit.com/r/uofm/comments/620fjd/thoughts_on_eecs388/ |
| 42 | EECS 388 versus EECS 485 discussion | Reddit r/uofm thread | `documents/eecs388/03_reddit_388_vs_485.txt`, https://www.reddit.com/r/uofm/comments/1n24wo6/eecs_388_vs_485/ |
| 43 | EECS 445 class pairing discussion | Reddit r/uofm thread | `documents/eecs445/02_reddit_445_pairing.txt`, https://www.reddit.com/r/uofm/comments/1avscoh/how_is_eecs_445_classes_to_pair_with_it/ |
| 44 | EECS 485 and EECS 445 workload discussion | Reddit r/uofm thread | `documents/eecs445/03_reddit_485_445_workload.txt`, https://www.reddit.com/r/uofm/comments/1s3xams/eecs485_eecs445_workload/ |
| 45 | EECS 485 and EECS 481 workload comparison | Reddit r/uofm thread | `documents/eecs481/02_reddit_485_481_workload.txt`, https://www.reddit.com/r/uofm/comments/15kvndb/eecs_485_481_workload_and_difficulty/ |
| 46 | EECS 489 experience discussion | Reddit r/uofm thread | `documents/eecs489/02_reddit_489_experience.txt`, https://www.reddit.com/r/uofm/comments/1p8jka4/eecs_489_experience/ |
| 47 | EECS 493 workload discussion | Reddit r/uofm thread | `documents/eecs493/02_reddit_493_workload.txt`, https://www.reddit.com/r/uofm/comments/1aw8754/eecs493/ |
| 48 | EECS 494 questions discussion | Reddit r/uofm thread | `documents/eecs494/02_reddit_494_questions.txt`, https://www.reddit.com/r/uofm/comments/1fuh8y0/eecs_494_questions/ |

## Pipeline

### Ingestion and Cleaning

The ingestion script recursively reads `.txt` files from `documents/`, so source notes can be organized by course number. Each file starts with:

```text
Title:
Source URL: or Source URLs:
Source Type:
Date Collected:
```

The cleaning step decodes HTML entities, removes HTML tags if any are present, removes common boilerplate words, normalizes whitespace, and keeps course-selection content such as prerequisites, projects, grading, topics, instructor history, workload comments, and support resources. For Reddit sources, I summarized public discussion content and kept the source URL so the notes are traceable without treating one comment as universal truth.

### Chunking Strategy

Chunking method: paragraph-aware character chunks.

- Chunk size: 750 characters
- Overlap: about 150 characters, implemented as paragraph/sentence-aware overlap instead of cutting in the middle of words
- Final chunk count: 99 chunks

I used 750 characters because my documents are short cleaned notes, not long PDFs. A smaller chunk keeps one course feature together, such as "EECS 485 has five projects" or "EECS 388 requires EECS 281." I used overlap because course names and details sometimes sit in adjacent paragraphs. I also changed the chunker after inspection because the first version split words in the middle, which made sample chunks look messy.

### Sample Chunks

1. Source: EECS 280 course homepage source notes  
   Chunk: "The homepage says students build several substantial programs: a statistical analysis tool, an image processing program, a Euchre card game, a machine learning algorithm, and a text editor. That makes EECS 280 a project-heavy course compared with a class that is mainly exams or short homework."

2. Source: EECS 281 course homepage source notes  
   Chunk: "The projects emphasize graph search and route tracing with BFS and DFS; priority queues, templated containers, inheritance, interface programming, and streaming algorithms; hash tables and larger data structures through composition; and optimization algorithms such as traveling salesperson and knapsack."

3. Source: EECS 370 assignments source notes  
   Chunk: "Lab topics visible on the assignments page include Binary and C, LC2K ISA, ARM Assembly, Linking and Functions, Digital Logic, Single and Multi-Cycle Datapaths, Pipelining, Datapath Performance, Caches, Cache-aware Programming, and Virtual Memory."

4. Source: EECS 388 course overview source notes  
   Chunk: "The prerequisites section says EECS 281 is required, and EECS 201 and EECS 370 are recommended. That makes EECS 388 a better choice after a student has algorithms and some systems background."

5. Source: EECS 485 syllabus source notes  
   Chunk: "Project 1 is a templated static site generator for an Instagram clone. Project 2 is server-side dynamic pages for an Instagram clone. Project 3 is client-side dynamic pages for an Instagram clone. Project 4 is MapReduce... Project 5 is a scalable search engine similar to Google or Bing."

6. Source: EECS 493 user interface development source notes  
   Chunk: "For course selection, EECS 493 is a good fit for students interested in HCI, UI/UX, user-centered design, interface implementation, usability, and testing user interfaces."

7. Source: EECS 482 operating systems source notes  
   Chunk: "The objective is to teach issues involved in the design and implementation of modern operating systems. For course selection, EECS 482 is a good fit for students who want operating systems, system design, concurrency, memory, processor management, file systems, and lower-level software infrastructure."

8. Source: EECS 489 computer networks source notes  
   Chunk: "For course selection, EECS 489 is a strong fit for students interested in networking, Internet architecture, distributed systems basics, sockets, routing, congestion, TCP/UDP, and client-server or peer-to-peer applications."

## Embedding Model

Model used: `sentence-transformers/all-MiniLM-L6-v2`.

Vector store: ChromaDB.

Top-k: 5.

I chose `all-MiniLM-L6-v2` because it runs locally and is fast for a small class-guide corpus. I also added a local `HashingVectorizer` fallback so the demo can still run if the Hugging Face model is not cached, but the intended embedding model is MiniLM.

Production tradeoff reflection: for a real deployment I would compare retrieval accuracy, cost, latency, model size, context length, privacy, and support for informal student language. A larger API model might retrieve better on slang or professor nicknames, but it would cost money and send data over the network. A local model is cheaper and more private, but less powerful.

## Retrieval Tests

### Retrieval Test 1

Query: `Which course should I take if I want full stack web development projects?`

Top returned chunks:

1. EECS 485 course homepage source notes, chunk 3, distance 0.422: says EECS 485 is a good match for full-stack applications and practical web engineering.
2. EECS 485 syllabus source notes, chunk 2, distance 0.433: says EECS 485 is good for full-stack web systems, distributed systems basics, and search-engine implementation.
3. EECS 485 and EECS 481 Reddit workload comparison source notes, chunk 0, distance 0.462: says EECS 485 may be heavier and more project-intensive than EECS 481.

Why relevant: the top two chunks directly answer the query by naming EECS 485 and explaining the web/full-stack project fit. The third chunk adds student workload context for the same course.

### Retrieval Test 2

Query: `EECS 388 security prerequisites EECS 281 EECS 370`

Top returned chunks:

1. EECS 388 course overview source notes, chunk 0, distance 0.284: describes EECS 388 as Introduction to Computer Security.
2. EECS 388 course overview source notes, chunk 3, distance 0.285: says EECS 388 fits students interested in security and is not a first systems course.
3. EECS 388 course overview source notes, chunk 2, distance 0.288: says EECS 281 is required and EECS 201/370 are recommended.

Why relevant: all top chunks come from the EECS 388 document and cover both the course topic and prerequisites.

### Retrieval Test 3

Query: `Which course has cache simulator assembly and low level computer organization projects?`

Top returned chunks:

1. EECS 370 assignments source notes, chunk 1, distance 0.366: lists ARM Assembly, datapaths, caches, cache-aware programming, and virtual memory labs.
2. EECS 370 assignments source notes, chunk 0, distance 0.392: lists assembler, simulator, linker, pipelined datapath simulator, and data/memory cache simulator projects.
3. EECS 370 course homepage source notes, chunk 2, distance 0.419: says EECS 370 is about low-level representation, assembly, datapaths, memory, and architecture.

Why relevant: the query asks for low-level computer organization and cache/assembly work, and the top results all point to EECS 370.

## Grounded Generation

System prompt grounding instruction:

```text
Answer only from the retrieved source excerpts.
If the excerpts do not contain enough information to answer, say:
"I don't have enough information in the collected documents to answer that."
Do not use outside knowledge.
Mention source titles naturally in the answer when they support a claim.
```

Source attribution is surfaced two ways. First, the LLM prompt asks for source titles in the answer. Second, the pipeline appends the source list programmatically after the generated answer, so citations are still visible even if the model forgets.

For the final demo, I use the Groq API with `llama-3.3-70b-versatile` for grounded generation. If `GROQ_API_KEY` is missing, the app still has a local extractive fallback for debugging, but that is not the intended final demo mode.

### Example Responses

#### Example 1

Question: `EECS 485 projects Instagram Google clone prerequisite`

Response:

```text
EECS 485 is the best match for this question. The EECS 485 course homepage says students build an Instagram clone in the first half of the semester and a Google clone in the second half. The EECS 485 syllabus also says the course requires EECS 281 and expects students to learn tools like HTML, CSS, SQL, Python, and JavaScript.

Sources:
- EECS 485 course homepage source notes (https://eecs485.org/)
- EECS 485 syllabus source notes (https://eecs485.org/syllabus.html)
```

#### Example 2

Question: `EECS 388 security prerequisites EECS 281 EECS 370`

Response:

```text
EECS 388 is Introduction to Computer Security. The EECS 388 source says EECS 281 is required, and EECS 201 and EECS 370 are recommended. Based on the retrieved source, it is a better fit after a student has algorithms and some systems background.

Sources:
- EECS 388 course overview source notes (https://eecs388.org/)
```

### Out-of-Scope Refusal

Question: `Where should I get pizza near campus?`

Response:

```text
I don't have enough information in the collected documents to answer that.
```

## Query Interface

Interface: Streamlit web app in `app.py`.

Input field:

- `Question`: a plain-language course-selection question.

Output fields:

- `Grounded Answer`: grounded response from retrieved source excerpts.
- `Sources Used`: source documents used for attribution.
- `Retrieved Chunks`: top chunks, source file paths, and distance scores for debugging/evaluation.

Sample transcript:

```text
User: Which course has cache simulator assembly and low level computer organization projects?

System: EECS 370 is the best match. The retrieved source says EECS 370 includes assembler/simulator work, a pipelined datapath simulator, a cache simulator, ARM Assembly, datapaths, cache-aware programming, and virtual memory.

Sources:
- EECS 370 assignments source notes (https://eecs370.github.io/resources/projects_hws.html)
- EECS 370 course homepage source notes (https://eecs370.github.io/)
```

## Evaluation Report

| # | Question | Expected answer | Retrieved chunks | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------|------------------------------|-------------------|-------------------|
| 1 | Which course should I take if I want full stack web development projects? | EECS 485, because it covers front end/back end and has web projects. | EECS 485 homepage chunk 3; EECS 485 syllabus chunk 2; EECS 485/481 Reddit workload chunk 0 | Recommended EECS 485 for full-stack web applications and practical web engineering. | Relevant | Accurate |
| 2 | EECS 388 security prerequisites EECS 281 EECS 370 | EECS 388 is the security course; EECS 281 is required and EECS 201/370 are recommended. | EECS 388 chunks 0, 3, 2 | Identified EECS 388 and included the EECS 281 required / EECS 201 and 370 recommended prerequisite info. | Relevant | Accurate |
| 3 | EECS 281 algorithms projects graph search priority queues hash tables | EECS 281 covers algorithms and projects with graph search, priority queues, hash tables, and optimization. | EECS 281 homepage chunks 3 and 1; EECS 281 syllabus chunk 1 | Returned EECS 281 and listed graph search, priority queues, hash tables, and optimization projects. | Relevant | Accurate |
| 4 | Who was the EECS 442 professor in 2025 winter term? | Stella Yu was the professor/instructor for EECS 442 Computer Vision in Winter 2025. | EECS 442 Winter 2025 Stella Yu teaching source chunk 0; EECS 370 homepage chunk 0; EECS 485 homepage chunk 0 | Answered Stella Yu and cited the EECS 442 Winter 2025 teaching source. | Relevant | Accurate |
| 5 | What math background does EECS 445 warn students need? | EECS 445 warns students need linear algebra and probability background. | EECS 388 chunks 2 and 3; EECS 376 Reddit learning chunk 0 | Incorrectly answered with EECS 388 prerequisite/security context instead of EECS 445 math background. | Off-target | Inaccurate |

## Failure Case Analysis

Question that failed: `What math background does EECS 445 warn students need?`

What the system returned: it returned EECS 388 prerequisite/security context instead of the EECS 445 math warning.

Root cause: this was a retrieval failure. The embedding search treated "background" and "need" as a generic prerequisite or theory-preparation question and matched EECS 388 and EECS 376 chunks more strongly than the EECS 445 math chunk. The EECS 445 source did contain the right answer, but the query wording did not include the exact terms "linear algebra" or "probability."

What I would change: I would add hybrid search with keyword matching for course numbers like "EECS 445" so that a query naming a course strongly prefers chunks from that course. I would also add metadata filtering by course number.

## Spec Reflection

One way the spec helped me during implementation: writing the chunk size and top-k before coding made it easier to check whether the pipeline matched the plan. When the first chunk output had words cut in half, I could compare it against my own chunking goal and fix the chunker instead of pretending it was fine.

One way my implementation diverged from the spec, and why: I first planned to use professor-review pages from Rate My Professors and Reddit, but Rate My Professors was not reliable to collect automatically and broad professor-review content was uneven. I changed the document set to public course pages, syllabi, faculty pages, and public r/uofm course-discussion threads. This makes the system better for course selection than subjective professor ratings alone.

## AI Usage

**Instance 1**

- What I gave the AI: I described the UMich CS course-selection domain and the starter repo requirements.
- What it produced: Codex scaffolded ingestion, chunking, ChromaDB indexing, retrieval, grounded generation, and a Streamlit interface.
- What I changed or overrode: I changed the input folder to match the starter repo's `documents/` folder, changed chunking from a rough character overlap to paragraph/sentence-aware overlap, and added an extractive fallback for demos without a Groq key.

**Instance 2**

- What I gave the AI: I gave the grading rubric and asked it to help structure the README so every required section was covered.
- What it produced: A README outline with sections for sources, chunking, retrieval tests, grounded generation, evaluation, failure analysis, and AI usage.
- What I changed or overrode: I filled in actual query results from my own runs, marked one result inaccurate, and wrote the failure explanation based on what the retrieval output showed.

**Instance 3**

- What I gave the AI: I asked it to expand the source set and organize the files by EECS course number.
- What it produced: Additional cleaned source notes for courses like EECS 203, 285, 376, 441, 473, 481, 482, 489, 492, 493, and 494, plus a recursive document loader and expanded Reddit discussion notes.
- What I changed or overrode: I kept the source notes tied to public URLs, kept Reddit notes framed as student anecdotes, kept the source files grouped by course folder, rebuilt the index, and reran retrieval tests to make sure the larger corpus still returned grounded answers.

## How to Run

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add your Groq key for LLM generation.

```bash
cp .env.example .env
```

Edit `.env` and set `GROQ_API_KEY`. The app has a fallback for debugging without a key, but the final demo should use the Groq API.

Build the vector index:

```bash
python -m src.build_index
```

Test retrieval:

```bash
python -m src.retrieve "Which course should I take if I want full stack web development projects?"
```

Ask a grounded question from the command line:

```bash
python -m src.query "EECS 388 security prerequisites EECS 281 EECS 370"
```

Run the web interface:

```bash
streamlit run app.py
```

Open the printed local URL, usually `http://localhost:8501`.
