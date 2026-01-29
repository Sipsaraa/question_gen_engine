# Contributing to Question Generation Engine

Thank you for your interest in contributing! We appreciate your efforts to make this project better.

## 🚀 How to Contribute

### 1. Reporting Bugs

- Check the [Issue Tracker](https://github.com/yourusername/question_gen_engine/issues) to see if the bug has already been reported.
- If not, open a new issue using the **Bug Report** template.
- Provide as much detail as possible (OS, exact steps to reproduce, error logs).

### 2. Suggesting Enhancements

- Open a new issue and describe your idea clearly.
- Explain the benefit and possible implementation approach.

### 3. Pull Requests

1. **Fork** the repository.
2. Create a new branch: `git checkout -b feature/my-new-feature` or `fix/bug-fix`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/my-new-feature`.
5. Open a **Pull Request**.

## 🛠 Development Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourusername/question_gen_engine.git
   cd question_gen_engine
   ```

2. **Set up Virtual Environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Services**
   Use Docker Compose for a consistent environment:
   ```bash
   docker compose up --build
   ```

## 📝 Code Style

- We use **Python 3.11+**.
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines.
- Add type hints to function signatures.
- Ensure your code is well-documented.

## ✅ Testing

Before submitting a PR, please ensure all tests pass (if applicable) and the application starts up correctly.

Thank you for your contributions!
