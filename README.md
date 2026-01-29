# Question Generation Engine

Welcome to the **Question Generation Engine**, a microservices-based system designed to automatically generate educational questions from syllabus content or PDF documents using advanced LLMs (Gemini, Groq).

## 🚀 Features

- **Multi-Model Support**: Leverages Google Gemini and Groq (Llama 3) for high-quality generation.
- **Microservices Architecture**: Decoupled services for Gateway, Question Bank, Generation, and Authentication.
- **PDF Processing**: Upload chapters as PDFs and automatically generate structured questions.
- **Question Bank**: Persist, manage, and export generated questions.
- **Authentication**: Secure admin access and API key management for external clients.
- **Documentation**: Comprehensive architecture diagrams and API docs.

## 🏗 Architecture

The system consists of the following services:

- **Gateway**: Entry point, service discovery, and routing.
- **Auth**: Manages admin users and API keys.
- **Generator**: Interacts with LLMs to create content.
- **QBank**: Stores and retrieves questions (CRUD).
- **Database**: Shared PostgreSQL instance.

See [docs/architecture.md](docs/architecture.md) for detailed diagrams and schema.

## 🛠 Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- Python 3.11+ (for local development)
- API Keys for Google AI Studio and Groq

## ⚡ Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/question_gen_engine.git
   cd question_gen_engine
   ```

2. **Configure Environment**
   Copy the example environment file and add your API keys:

   ```bash
   cp .env.example .env
   # Edit .env and fill in GOOGLE_API_KEY and GROQ_API_KEY
   ```

3. **Start with Docker Compose**

   ```bash
   docker compose up --build
   ```

4. **Access the Application**
   - **Gateway API**: [http://localhost:8000](http://localhost:8000)
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Architecture Docs**: [http://localhost:8000/help](http://localhost:8000/help) (if mounted)

## 📖 Documentation

- **Architecture**: `docs/architecture.md`
- **Authentication**: `docs/authentication.md`
- **Service Guides**: `docs/services/`

To run documentation locally:

```bash
pip install mkdocs-material
mkdocs serve
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to help improve this project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
