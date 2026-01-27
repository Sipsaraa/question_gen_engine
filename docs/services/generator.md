# Generator Service

The Generator service uses AI to create questions from syllabus content or uploaded documents.

## API Endpoints

### Generate from Text

Generate questions based on valid syllabus content provided in the JSON body.

**Endpoint:** `POST /generate`

**Request Body (`SyllabusContent`):**

| Field             | Type     | Description                                        |
| :---------------- | :------- | :------------------------------------------------- |
| `subject`         | `string` | Subject name                                       |
| `grade`           | `string` | Grade level                                        |
| `medium`          | `string` | Medium of instruction                              |
| `chapter_id`      | `string` | ID of the chapter                                  |
| `chapter_name`    | `string` | Name of the chapter                                |
| `content`         | `string` | The actual text content to generate questions from |
| `generation_type` | `string` | 'general' (default)                                |

**Example Request:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "subject": "science",
  "grade": "10",
  "medium": "english",
  "chapter_id": "CH05",
  "chapter_name": "Photosynthesis",
  "content": "Photosynthesis is the process by which green plants define their own food using sunlight.",
  "generation_type": "general"
}'
```

---

### Generate from PDF

Upload a PDF file to extract text and generate questions.

**Endpoint:** `POST /generate/pdf`

**Form Data:**

| Field          | Type     | Description           |
| :------------- | :------- | :-------------------- |
| `file`         | `file`   | The PDF document      |
| `subject`      | `string` | Subject name          |
| `grade`        | `string` | Grade level           |
| `medium`       | `string` | Medium of instruction |
| `chapter_id`   | `string` | ID of the chapter     |
| `chapter_name` | `string` | Name of the chapter   |

**Example Request:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/generate/pdf' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/textbook_chapter.pdf;type=application/pdf' \
  -F 'subject=science' \
  -F 'grade=10' \
  -F 'medium=english' \
  -F 'chapter_id=CH05' \
  -F 'chapter_name=Photosynthesis'
```
