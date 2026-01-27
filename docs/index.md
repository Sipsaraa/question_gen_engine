# Question Generation Engine

Welcome to the documentation for the Question Generation Engine. This project is a microservices-based application designed to generate and manage educational questions.

## Quick Start

### Prerequisites

- Python 3.10+
- Docker (optional, for containerized run)

### Installation

1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Services

The easiest way to run the entire system (Gateway + QBanks + Generator) is to use the provided script:

```bash
python scripts/start_services.py
```

This will:

1.  Start the **Gateway** on port `8000`.
2.  Start specialized **QBank Services** (General, Science, Maths, History) on ports `8010` onwards.
3.  Start the **Generator Service** on port `8004`.

You can then access the Gateway API docs at: http://127.0.0.1:8000/docs

## Features

- **Question Banking**: Store and retrieve questions based on subject, grade, medium, etc.
- **AI Generation**: Generate validation questions from syllabus content or PDF uploads.
- **PDF Export**: Export selected questions to a formatted PDF.
