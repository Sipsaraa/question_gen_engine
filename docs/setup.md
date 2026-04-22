# Setup Guide

Guidelines for configuring and running the Question Generation Engine.

## Configuration

The service is configured via environment variables in the `.env` file.

### Required Variables

| Variable              | Description                          | Default  |
| --------------------- | ------------------------------------ | -------- |
| `GROQ_API_KEY`        | API Key from Groq Console            | Required |
| `QT_INTERNAL_API_KEY` | Key for authenticating service calls | Required |
| `PRIMARY_GENERATOR`   | Primary model provider               | `groq`   |
| `FALLBACK_GENERATOR`  | Fallback model provider              | `groq`   |
| `GENERATOR_PORT`      | Port for the FastAPI server          | `8004`   |

## Local Setup

Ensure you have [uv](https://docs.astral.sh/uv/) installed.

1. **Sync Dependencies**:

   ```bash
   make dev-setup
   ```

2. **Run Environment**:

   ```bash
   make up-build
   ```

3. **Verify Generation**:
   You can verify the core engine by running the verification scripts (if available) or by calling the `/generate` endpoint directly.

## Deployment

The engine is distributed with a `Dockerfile` optimized for production using `uv`. Use `docker-compose.yml` for orchestration.
