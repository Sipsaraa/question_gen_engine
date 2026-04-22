# Sipsaraa - Question Generation Engine

A streamlined, stateless engine powered by Groq (Llama 3.3) for generating high-quality educational questions.

## Features

- **Stateless Architecture**: Zero persistence; request-in, questions-out.
- **Groq Integration**: High-speed generation using `llama-3.3-70b-versatile`.
- **Physics Mode**: Enhanced LaTeX support and conceptual depth for science content.
- **MDX Support**: Explanations formatted in MDX for rich rendering.
- **Dockerized**: Easy deployment with `uv` and `docker-compose`.

## Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- [Groq API Key](https://console.groq.com/)
- Python 3.12+ (if running locally)

## Getting Started

### 1. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and provide your `GROQ_API_KEY`. You can also configure the `PRIMARY_GENERATOR` (default: `groq`).

### 2. Running with Docker

Start the engine:

```bash
make up-build
```

The engine will be available at [http://localhost:8004](http://localhost:8004).

## Documentation

The service includes a built-in documentation site. To view it:

1. **Start with Docker**: `make up-build`
2. **Access**: [http://localhost:8005](http://localhost:8005)

Alternatively, run locally: `make docs-serve`.

## API Usage

#### POST `/generate`

Generates structured questions from content.

**Request Body:**

```json
{
  "subject": "Physics",
  "grade": "12",
  "medium": "English",
  "content": "Kinematics is the branch of mechanics...",
  "generation_type": "physics",
  "chapter_id": 1,
  "chapter_name": "Unit 1"
}
```

## Development

Set up the local environment using `uv`:

```bash
make dev-setup
```

Run tests:

```bash
make test
```

Check code style:

```bash
make lint
```

## License

This project is licensed under the MIT License.
