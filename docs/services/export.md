# Export Service

The Export service allows you to compile existing questions from the QBank into a downloadable PDF document.

## API Endpoints

### Export to PDF

Fetch questions matching the criteria and return a PDF file.

**Endpoint:** `GET /questions/export/pdf`

**Parameters:**

| Parameter    | Type      | Description                                                     |
| :----------- | :-------- | :-------------------------------------------------------------- |
| `subject`    | `string`  | **Required**. Subject to export questions for via Subject QBank |
| `grade`      | `string`  | **Required**. Grade level filter                                |
| `medium`     | `string`  | **Required**. Medium filter                                     |
| `chapter_id` | `string`  | **Required**. Chapter ID filter                                 |
| `start_id`   | `integer` | optional - Start range of Question IDs                          |
| `end_id`     | `integer` | optional - End range of Question IDs                            |

**Example Request:**

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/questions/export/pdf?subject=science&grade=10&medium=english&chapter_id=CH01' \
  -H 'accept: application/pdf' \
  --output questions_science_CH01.pdf
```

This command will download the file and save it as `questions_science_CH01.pdf`.
