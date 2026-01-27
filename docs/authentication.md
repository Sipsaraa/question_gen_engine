# Authentication System

The Question Generation Engine uses a robust, tiered authentication system designed for microservices. It balances security with ease of use for client applications.

## Overview

The system distinguishes between two types of access:

1.  **Admin Access**: Human administrators who manage the system and issue API keys. Authenticated via Username/Password.
2.  **Service/Client Access**: Applications (e.g., Mobile App, Frontend) that consume the API. Authenticated via long-lived **API Keys**.

### Security Model

- **Token Based**: All authentication uses JWTs (JSON Web Tokens).
- **Revocable**: API Keys are standard JWTs but are also tracked in the database. This allows admins to instantly revoke any key, preventing further access even if the token hasn't expired.
- **Centralized**: All auth requests are handled by the dedicated `Auth Service`, but the Gateway acts as the enforcement point.

---

## 1. Setting Up an Admin

Before you can use the system, you must create at least one admin user. This is done via a secure CLI script running on the server.

### Run the Creation Script

Access the server terminal (or run inside the Docker container) and execute:

```bash
# Provide a unique username and a strong password
python scripts/create_admin.py --user admin --pass MySecurePassword123
```

> **Note**: If running locally with Docker Compose, you may need to use the python environment inside the container or ensure your local environment has the necessary dependencies (`passlib`, `bcrypt`, `sqlalchemy`, `psycopg2`).
>
> **Docker Command Example**:
>
> ```bash
> docker compose exec -it auth python /app/scripts/create_admin.py --user admin --pass MySecurePassword123
> ```

---

## 2. API Key Management

Once an admin account exists, you can generate API keys for your applications. These keys are what you will typically use in your HTTP headers.

### Login as Admin

First, obtain a temporary session token (Admin Token).

**Request:**

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=MySecurePassword123
```

**Response:**

```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer"
}
```

### Create an API Key

Use the Admin Token to generate a long-lived API Key.

**Request:**

```http
POST /auth/api-keys
Authorization: Bearer <ADMIN_TOKEN>
Content-Type: application/json

{
  "name": "Mobile Frontend V1",
  "permissions": ["generate", "read"]
}
```

**Response:**

```json
{
  "key_id": "550e8400-e29b...",
  "name": "Mobile Frontend V1",
  "access_token": "eyJhbG... (Save this!)",
  "created_at": "2023-10-27T10:00:00"
}
```

> **Important**: The `access_token` returned here is your **API Key**. It resolves to the `key_id` internally.

### Revoking a Key

If a key is compromised, revoke it immediately.

**Request:**

```http
DELETE /auth/api-keys/{key_id}
Authorization: Bearer <ADMIN_TOKEN>
```

---

## 3. Using API Keys

To access protected endpoints (like `/generate`), include the API Key in the `Authorization` header.

### Example Request using cURL

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Authorization: Bearer <YOUR_API_KEY>" \
     -H "Content-Type: application/json" \
     -d '{
           "subject": "Biology",
           "grade": "10",
           "medium": "English",
           "chapter_id": "ch1",
           "chapter_name": "Photosynthesis",
           "content": "Plants make food using sunlight...",
           "generation_type": "general"
         }'
```

### Authentication Errors

- **401 Unauthorized**: Missing or invalid token.
- **401 Unauthorized (Details)**: "API Key is revoked" -> The key format is valid, but it has been disabled by an admin.

---

## API Reference

| Method   | Endpoint              | Description                               | Auth Required     |
| :------- | :-------------------- | :---------------------------------------- | :---------------- |
| `POST`   | `/auth/token`         | Admin Login. Returns Admin Session Token. | No                |
| `POST`   | `/auth/api-keys`      | Create a new API Key.                     | **Yes** (Admin)   |
| `GET`    | `/auth/api-keys`      | List all issued API Keys.                 | **Yes** (Admin)   |
| `DELETE` | `/auth/api-keys/{id}` | Revoke/Disable an API Key.                | **Yes** (Admin)   |
| `POST`   | `/generate`           | Generate questions from content.          | **Yes** (API Key) |
| `POST`   | `/generate/pdf`       | Generate questions from PDF upload.       | **Yes** (API Key) |
