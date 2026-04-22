# Welcome to Question Gen Engine

The **Question Generation Engine** is a high-performance, stateless service designed to transform educational content into structured test items (MCQs, Fill-in-the-blanks, and Structured questions).

## Key Features

- **Stateless Design**: Easy to scale and integrate.
- **Groq Enhanced**: Leverages Llama 3.3 for superior pedagogical quality.
- **Physics Specialized**: Built-in support for LaTeX and physical law citations.
- **FastAPI Core**: Standard-compliant, high-speed API.

## Architecture Overview

The engine acts as a pure function:
`Input (Content + Metadata) -> Question Generator (Groq) -> Output (JSON Questions)`

Persistence and user management are handled by the calling application (e.g., Sipsaraa Django Backend).
