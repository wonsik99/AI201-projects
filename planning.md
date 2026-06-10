# Project 1 Planning: The Unofficial Guide

## Domain

I chose University of Michigan CS/EECS course selection. My first idea was professor reviews, but those were hard to collect from in a reliable way, so I am focusing on course pages, syllabi, assignment pages, faculty teaching pages, and public r/uofm threads that still help students decide what class fits them.

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
30. https://www.reddit.com/r/uofm/comments/1q9d894/eecs_281_workload_questions/
31. https://www.reddit.com/r/uofm/comments/rwpiyv/eecs_workload_check/
32. https://www.reddit.com/r/uofm/comments/162bmcv/words_of_wisdomadvice_on_eecs_370_485_and_how_to/
33. https://www.reddit.com/r/uofm/comments/uzdwqh/how_doable_is_eecs_370_and_eecs_376_for_fall/
34. https://www.reddit.com/r/uofm/comments/1mbzdyk/should_i_take_eecs_482/
35. https://www.reddit.com/r/uofm/comments/1hkyd62/eecs_485_web_systems_course_recommendationhonest/
36. https://www.reddit.com/r/uofm/comments/nxnp7k/preparing_for_eecs_203_and_eecs_280/
37. https://www.reddit.com/r/uofm/comments/17pgslq/eecs_280_calc_2_eecs_203_at_the_same_time/
38. https://www.reddit.com/r/uofm/comments/151lctq/eecs_280_rigor/
39. https://www.reddit.com/r/uofm/comments/6ycvju/eecs_280_workload/
40. https://www.reddit.com/r/uofm/comments/nayizd/how_are_the_eecs_280_projects_ranked/
41. https://www.reddit.com/r/uofm/comments/1dc4yi0/the_lazy_students_guide_to_eecs_281/
42. https://www.reddit.com/r/uofm/comments/a1edc6/eecs_280_vs_eecs_281_projectsautograder/
43. https://www.reddit.com/r/uofm/comments/l6nx27/how_bad_is_eecs_281/
44. https://www.reddit.com/r/uofm/comments/rru85c/eecs_270_vs_370_workload/
45. https://www.reddit.com/r/uofm/comments/4gm8wf/what_class_to_take_with_eecs_370/
46. https://www.reddit.com/r/uofm/comments/1ki1vy8/classes_to_take_with_eecs_376/
47. https://www.reddit.com/r/uofm/comments/lcsvga/eecs_376_sad/
48. https://www.reddit.com/r/uofm/comments/1gy7ih1/eecs_376_students_how_are_you_learning_the/
49. https://www.reddit.com/r/uofm/comments/620fjd/thoughts_on_eecs388/
50. https://www.reddit.com/r/uofm/comments/1n24wo6/eecs_388_vs_485/
51. https://www.reddit.com/r/uofm/comments/1avscoh/how_is_eecs_445_classes_to_pair_with_it/
52. https://www.reddit.com/r/uofm/comments/1s3xams/eecs485_eecs445_workload/
53. https://www.reddit.com/r/uofm/comments/15kvndb/eecs_485_481_workload_and_difficulty/
54. https://www.reddit.com/r/uofm/comments/1p8jka4/eecs_489_experience/
55. https://www.reddit.com/r/uofm/comments/1aw8754/eecs493/
56. https://www.reddit.com/r/uofm/comments/1fuh8y0/eecs_494_questions/

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

3. Reddit comments are useful because they are more unofficial, but they are also subjective. I should treat them as student anecdotes, not guaranteed facts.

## Architecture

My pipeline is basically:

documents folder -> clean text -> chunk text -> embed chunks -> store in ChromaDB -> retrieve top 5 chunks -> answer with sources -> show it in Streamlit

The main thing I need to remember is that the answer step should only use the retrieved chunks. If the chunks do not have the answer, the app should say it does not know instead of guessing.

## AI Tool Plan

Milestone 3 - Ingestion and chunking: I will ask Codex to write the document loader and chunker using my chunk size and overlap. I will check the printed sample chunks myself and change the code if chunks are cut off or hard to read.

Milestone 4 - Embedding and retrieval: I will ask Codex to connect `all-MiniLM-L6-v2` to ChromaDB and return top-k chunks with source metadata. I will test retrieval before adding generation because bad retrieval would make the answer bad no matter what model I use.

Milestone 5 - Generation and interface: I will ask Codex to make the answer use only retrieved chunks and show sources. I will also ask it to make a simple Streamlit interface with question input, answer output, source output, and retrieved chunk output.
