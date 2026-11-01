# External technical question dataset sources

## CodePrep Open Interview Questions

- Repository: https://github.com/codeprepdev/codeprep-questions
- Raw JSON: https://raw.githubusercontent.com/codeprepdev/codeprep-questions/main/data/questions.json
- Declared licence: CC-BY-4.0
- Published size: 110 questions across 11 technologies
- Includes: question prompt, difficulty label, question type, tags, answer
  payload, and explanation.
- Attribution required: `Questions from CodePrep (https://codeprep.dev), CC-BY-4.0.`

The ingestion pipeline supports its top-level metadata and structured answer
shapes. Before shipping imported records, review the source dataset version,
question types, answer quality, and the exact licence notice. Keep the source
attribution in each normalized record.

## Additional candidate: Data Science Interviews

- Repository: https://github.com/alexeygrigorev/data-science-interviews
- Declared licence: CC-BY-4.0
- Content: community-maintained data-science theory and technical questions.
- Caution: the repository states that answers are community-provided; review
  technical correctness before using them as grading references.

## Import policy

- Never infer or invent a licence.
- Preserve the original source name and URL per question.
- Record any modifications in the dataset description or project attribution.
- Manually review reference answers before using them for candidate scoring.
- Keep imported source datasets separate from the original MockMATE-curated
  questions so provenance remains traceable.
