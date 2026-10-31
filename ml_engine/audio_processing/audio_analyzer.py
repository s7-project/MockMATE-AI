from pathlib import Path

import whisper


class AudioAnalyzer:
    def __init__(self, model_name="base"):
        print("Loading Whisper audio model...")

        self.model = whisper.load_model(model_name)

        print("Whisper model loaded successfully!")

    def transcribe(self, audio_path):

        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        result = self.model.transcribe(str(path), fp16=False)

        return {
            "transcription": result["text"].strip(),
            "language": result.get("language"),
            "segments": result.get("segments", []),
        }


if __name__ == "__main__":
    analyzer = AudioAnalyzer(model_name="base")

    audio_file = input("Enter audio file path: ").strip()

    result = analyzer.transcribe(audio_file)

    print("\nTranscribed text:")
    print(result["transcription"])

    print("\nDetected language:")
    print(result["language"])
