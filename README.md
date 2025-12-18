# GitHub Repository Analyzer


---

## Overview

**GPT GitHub Repository Analyzer** is a Python Flask application that automatically analyzes GitHub repositories. It clones any public or private repository (with a token), reads the source code, and provides an AI-powered audit. The analysis includes:

- **Code Quality & Architecture:** Reviews project structure, maintainability, and coding standards.
- **Security Analysis:** Detects potential vulnerabilities, hardcoded secrets, and unsafe practices.
- **Health Score:** Assigns a score (0–100) representing the overall quality and security of the repository.
- **Summary & Roadmap:** Generates a concise 3-sentence summary and actionable 3–5 point roadmap.
- **Structured Output:** JSON format for easy integration into dashboards, CI/CD pipelines, or automation workflows.

---

## Features

- Supports **public and private GitHub repositories**
- Limits very large files to avoid GPT token overflow
- Provides **Health Score**, **Summary**, and **Roadmap**
- Handles sensitive keys via `.env` (never committed)
- Extensible for additional analysis features (dependency checks, license compliance, etc.)

---

## Tech Stack

- **Backend:** Python, Flask  
- **AI Integration:** OpenAI GPT API (`gpt-4.1-mini`)  
- **Repository Handling:** GitPython  
- **Environment Management:** python-dotenv  
- **Frontend:** Flask templates (HTML/CSS)

---
# GitHub Analyzer Setup Guide

## Installation

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

- **Windows:** `venv\Scripts\activate`
- **Linux/macOS:** `source venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```bash
OPENAI_API_KEY=
GITHUB_TOKEN=
```

## Usage

1. **Start the Flask app:**

```bash
python app.py
```

2. **Open your browser at** `http://127.0.0.1:5000`

3. **Enter the GitHub repository URL** you want to analyze.

4. **Receive AI-generated analysis** including health score, summary, roadmap, and detailed findings in JSON format.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for details.
