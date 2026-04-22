# API Reference

The Question Generation Engine exposes a single primary endpoint for generating content.

## Generate Questions

`POST /generate`

Main endpoint to transform syllabus content into structured questions.

### Authentication

All requests must include an internal API key in the header:

- **Header**: `X-API-Key`
- **Value**: Your `QT_INTERNAL_API_KEY` (configured in `.env`)

### Request Body

```json
{
  "subject": "string", // Subject name (e.g., Physics)
  "grade": "string", // Grade level (e.g., 12)
  "medium": "string", // Language (English, Sinhala, Tamil)
  "chapter_id": "string", // External reference ID for the chapter
  "chapter_name": "string", // Human readable chapter name
  "content": "string", // The raw text content to generate from
  "generation_type": "string" // "general" or "physics"
}
```

### Response Example

Returns a list of `GeneratedQuestion` objects.

```json
[
  {
    "subject": "Physics",
    "grade": "12",
    "medium": "English",
    "chapter_id": "CH-101",
    "chapter_name": "Kinematics",
    "question_type": "mcq",
    "question_text": "What is the unit of Force?",
    "options": "[\"Newton\", \"Joule\", \"Watt\", \"Volt\"]",
    "answer": "[\"Newton\"]",
    "explanation": "Calculated as Mass x Acceleration..."
  }
]
```
