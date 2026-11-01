"""Command-line utility to validate and normalize external JSON datasets.

Usage:
    python -m mockmate_ml.data.ingest input.json output.json --name "Dataset name"

Input may be a JSON array, JSONL, or an object containing a ``questions``
array and optional dataset-level provenance metadata.
"""

import argparse
import json
from pathlib import Path
from typing import Any

from mockmate_ml.data.loader import ingest_records, write_dataset


def read_records(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        payload = [
            json.loads(line)
            for line in raw_text.splitlines()
            if line.strip()
        ]

    metadata: dict[str, Any] = {}
    if isinstance(payload, dict):
        metadata = payload
        payload = payload.get("questions")

    if not isinstance(payload, list) or not all(
        isinstance(item, dict) for item in payload
    ):
        raise ValueError(
            "Input must be a JSON array or an object with a questions array."
        )
    return payload, metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and ingest interview questions."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--name", required=True, help="Dataset name")
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument(
        "--description", default="Imported technical interview questions"
    )
    parser.add_argument("--source-name", default=None)
    parser.add_argument("--source-url", default=None)
    parser.add_argument("--license", default=None)
    args = parser.parse_args()

    records, metadata = read_records(args.input)
    source_name = args.source_name or metadata.get("attribution")
    source_url = args.source_url or metadata.get("source")
    license_name = args.license or metadata.get("license")

    dataset = ingest_records(
        records,
        dataset_name=args.name,
        dataset_version=args.version,
        description=args.description,
        default_source_name=source_name,
        default_source_url=source_url,
        default_license=license_name,
    )
    output = write_dataset(dataset, args.output)
    print(
        f"Validated {len(dataset.questions)} questions from "
        f"{dataset.dataset_name!r}; wrote {output}"
    )


if __name__ == "__main__":
    main()
