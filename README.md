<p align="center"><img src="static/img/logo-light.png" alt="Solvely" height="80"></p>

# Solvely: Math Word Problem Solver (LLM Mini Project)

**Live demo:** https://solvely-tutor.vercel.app

**Problem statement:** Students struggle with word problems. This app solves a math word problem step by step, explains each step in simple words, and verifies the arithmetic with Python (SymPy).

## How it works
1. Student types a word problem (or picks a topic from the index) in the web UI.
2. A prompt (system rules + one worked example = few-shot) asks the LLM to "think step by step" and end with two fixed lines:
   `EXPRESSION: <pure arithmetic>` and `FINAL ANSWER: <number> <unit>`.
3. The LLM (GPT-OSS 120B via the free Groq API) returns the solution.
4. The app parses the output, re-computes `EXPRESSION` with **SymPy** (only digits and operators allowed, so no unsafe `eval`) and compares it with the final answer (= verified / ≠ mismatch).
5. The UI shows the result as an exam-style answer sheet: the question, a Data / Required table, numbered steps, a boxed final answer and a SymPy "checked" stamp. **Learn mode** reveals one step at a time and hides the answer until the student has tried each step.
6. **Dark mode** (follows the system setting; toggle with the theme button or `D`) and **Solve history** (saved in the browser, searchable, reopens past solutions without another API call; open with the History button or `H`).

## Tech stack
Python, FastAPI, HTML/CSS/JavaScript (custom UI), Groq API (`openai/gpt-oss-120b`), SymPy, python-dotenv

## How to run
```bash
pip install -r requirements.txt
copy .env.example .env      # then put your free key from https://console.groq.com/keys
python app.py              # opens http://localhost:8000
```

## Files
| File | Purpose |
|---|---|
| `app.py` | FastAPI server (`/api/solve`) |
| `static/index.html` | Web UI: hero, question slip (ruled paper, live "numbers spotted" strip, tick-box modes), topic index, exam-style answer sheet (margin-numbered steps, boxed answer, SymPy stamp), Learn mode, equation explainer |
| `solver.py` | Prompt, LLM call, output parsing, SymPy verification |
| `requirements.txt` | Dependencies |
| `.env.example` | Template for the API key (real `.env` is git-ignored) |
| `report/report.html` | Source of the 2-page procedure report (`Report.pdf`) |

## Screenshots
![home](screenshots/1_home.jpg)
![answer sheet](screenshots/2_answer_sheet.jpg)
![answer](screenshots/3_answer_box.jpg)
![learn mode, dark](screenshots/4_learn_mode_dark.jpg)
