import os
import json
import time
import traceback
import tempfile
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from git import Repo
from dotenv import load_dotenv
from openai import OpenAI

# ---------------- LOAD ENV ----------------
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY not found")

# ---------------- OPENAI CLIENT ----------------
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------- FLASK APP ----------------
app = Flask(__name__)
CORS(app)

# ---------------- CONFIG ----------------
MAX_FILES = 10
MAX_FILE_CHARS = 8000
SLEEP_BETWEEN_CALLS = 1.5

ALLOWED_EXT = {'.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.java', '.cpp'}
IGNORED_DIRS = {'.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build'}

# ---------------- SCORING LOGIC ----------------
def extract_severity_counts(analyses):
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for text in analyses:
        for level in counts:
            counts[level] += text.count(f"[{level}]")
    return counts


def calculate_health_score(counts):
    score = 100
    score -= counts["HIGH"] * 15
    score -= counts["MEDIUM"] * 7
    score -= counts["LOW"] * 3
    return max(score, 0)

# ---------------- FILE LOADER ----------------
def load_files(local_path):
    files_data = []

    for root, dirs, files in os.walk(local_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in ALLOWED_EXT:
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if 300 < len(content) < MAX_FILE_CHARS:
                            files_data.append({
                                "path": os.path.relpath(path, local_path),
                                "content": content[:MAX_FILE_CHARS]
                            })
                except:
                    pass

        if len(files_data) >= MAX_FILES:
            break

    return files_data[:MAX_FILES]

# ---------------- FILE ANALYSIS (RULE-BASED) ----------------
def analyze_file(file):
    findings = []

    content = file["content"]

    if "api_key" in content.lower():
        findings.append("[HIGH] Possible hardcoded API key detected → Move secrets to environment variables")

    if "except:" in content:
        findings.append("[MEDIUM] Bare except clause used → Catch specific exceptions")

    if "print(" in content:
        findings.append("[LOW] Debug print statements found → Replace with logging")

    if not findings:
        findings.append("[LOW] No major issues detected")

    return f"{file['path']}:\n" + "\n".join(findings)

# ---------------- FINAL SUMMARY (GPT) ----------------
def summarize_repo(file_results, score, counts):

    prompt = f"""
You are generating a final audit report.

FACTS (DO NOT CHANGE):
- Health score: {score}
- Issue counts:
  - HIGH: {counts['HIGH']}
  - MEDIUM: {counts['MEDIUM']}
  - LOW: {counts['LOW']}

VERIFIED FINDINGS:
{chr(10).join(file_results)}

TASK:
1. Write a 3-sentence executive summary that reflects the score and severity
2. Create a prioritized improvement roadmap:
   - Fix HIGH issues first
   - Then MEDIUM
   - Then LOW

RULES:
- Do NOT introduce new issues
- Every roadmap item must map to findings above

OUTPUT JSON ONLY:
{{
  "score": {score},
  "summary": "",
  "roadmap": ["..."],
  "details": ["..."]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=500
    )

    text = response.choices[0].message.content
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    repo_url = data.get("url")

    if not repo_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        with tempfile.TemporaryDirectory() as local_path:

            if "github.com" in repo_url and GITHUB_TOKEN:
                auth_url = repo_url.replace("https://", f"https://{GITHUB_TOKEN}@")
            else:
                auth_url = repo_url

            Repo.clone_from(auth_url, local_path)

            files = load_files(local_path)
            if not files:
                return jsonify({"error": "No readable source files found"}), 400

            file_results = []

            for f in files:
                file_results.append(analyze_file(f))
                time.sleep(SLEEP_BETWEEN_CALLS)

            severity_counts = extract_severity_counts(file_results)
            score = calculate_health_score(severity_counts)

            final_report = summarize_repo(
                file_results=file_results,
                score=score,
                counts=severity_counts
            )

            return jsonify(final_report)

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"error": str(e), "trace": tb}), 500

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
