"""Whisper transcription adapter with lazy optional dependency loading."""

from pathlib import Path
from typing import Any


class AudioTranscriber:
    def __init__(self, model_name: str = "base") -> None:
        try:
            import whisper
        except ImportError as exc:
            raise RuntimeError(
                "Audio transcription requires the optional 'audio' extra. "
                "Install it with: pip install -e './ml_engine[audio]'"
            ) from exc
        self._model: Any = whisper.load_model(model_name)

    def transcribe(self, audio_path: str | Path) -> dict[str, Any]:
        path = Path(audio_path)
        if not path.is_file():
            raise FileNotFoundError(f"Audio file not found: {path}")
        result = self._model.transcribe(str(path), fp16=False)
        return {
            "transcription": result["text"].strip(),
            "language": result.get("language"),
            "segments": result.get("segments", []),
        }
