# CodePath AI201 — Projects

Larger standalone projects from the CodePath AI201 course. (Smaller weekly labs
live in a separate repo: [`codepath-ai201`](https://github.com/wonsik99/codepath-ai201).)

## Projects

| # | Project | Description |
|---|---------|-------------|
| 1 | [The Unofficial Guide](./project1) | RAG system for choosing UMich CS/EECS courses with source-attributed answers |
| 2 | [FitFindr](./project2) | Outfit-recommendation agent over secondhand clothing listings and a user wardrobe |
| 3 | [TakeMeter](./project3) | Fine-tuned classifier for r/soccer discourse quality and comment type |
| 4 | [Provenance Guard](./project4) | Backend attribution system for distinguishing human-written and AI-generated creative text |
| 5 | [Mixtape Bug Hunt](./project5) | Flask social-music app bug hunt — find and fix service-layer bugs with RCA docs |
| 6 | [CineLog](./project6) | Simulated code review — respond to PR feedback, rebase onto a UUID refactor, rewrite commit history |

## How to run (each project)

```bash
cd projectN
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your API key to .env
python app.py
```
