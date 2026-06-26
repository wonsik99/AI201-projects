# Provenance Guard

Provenance Guard is a backend service for creative platforms that classifies submitted text as likely AI-generated, likely human-written, or uncertain, then exposes that decision through a transparency label, confidence score, appeal flow, and audit log.

## Project Summary

This project is about attribution, trust, and transparency on platforms where people share original writing. The system will combine at least two distinct detection signals, score uncertainty honestly, provide user-facing label text, accept appeals from creators, and record every decision in a structured audit log.

## Planned Features

- `POST /submit` for content attribution analysis
- Multi-signal detection pipeline
- Confidence scoring with an explicit uncertainty band
- Transparency label text for users
- Appeal submission and status updates
- Rate limiting on submission requests
- Structured audit log with decision history

## Working Files

- [planning.md](./planning.md)
- [requirements.txt](./requirements.txt)
- [src/](./src)

