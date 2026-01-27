# QBank Service

The Question Bank (QBank) service is responsible for storing and retrieving questions. The Gateway routes requests to the appropriate QBank instance (General, Science, Maths, etc.) based on the subject.

## API Endpoints

### List Questions

Retrieve a list of questions with optional filtering.

**Endpoint:** `GET /questions`

**Parameters:**

| Parameter    | Type     | Description                                              |
| :----------- | :------- | :------------------------------------------------------- |
| `subject`    | `string` | optional - Filter by subject (e.g., "science", "maths")  |
| `grade`      | `string` | optional - Filter by grade level                         |
| `medium`     | `string` | optional - Filter by medium (e.g., "english", "sinhala") |
| `chapter_id` | `string` | optional - Filter by specific chapter                    |

**Example Request:**

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/questions?subject=science&grade=10&medium=english' \
  -H 'accept: application/json'
```

**Example Response:**

```json
[
  {
    "id": 1,
    "subject": "science",
    "grade": "10",
    "medium": "english",
    "chapter_id": "CH01",
    "chapter_name": "Forces",
    "question_type": "mcq",
    "question_text": "What is the unit of Force?",
    "options": "[\"Newton\", \"Joule\", \"Watt\", \"Pascal\"]",
    "answer": "Newton",
    "explanation": "Force is measured in Newtons (N)."
  }
]
```
