# MockMATE ML Engine

AI-powered Python technical mock interview system.

## Features

1. Python technical question bank.
2. Topic-based question selection.
3. Difficulty-based question selection.
4. Semantic answer evaluation.
5. Keyword coverage.
6. Automated feedback.
7. Audio transcription using Whisper.
8. Video analysis using MediaPipe and OpenCV.

## Technologies

- Python
- Sentence Transformers
- PyTorch
- Whisper
- OpenCV
- MediaPipe

## Run the interview

From the MockMATE root directory:

python -m ml_engine.demo

## Run tests

python -m unittest discover -s ml_engine/tests -v