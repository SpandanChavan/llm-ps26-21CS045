# Math Word Problem Solver using LLM: Procedure Report
**Name:** Spandan Chavan  **Roll No:** 26  **PS No:** 26  **GitHub:** https://github.com/SpandanChavan/llm-ps26-21CS045

## 1. Problem Understanding
Students often understand arithmetic but fail to convert a word problem into the right sequence of operations. The goal is a tool that takes a word problem in plain English, solves it **step by step with an explanation of each step**, and gives a clear final answer. Because LLMs sometimes make arithmetic slips, the answer is **independently verified** with Python (SymPy).

## 2. Approach / Prompt Design
- **Model:** GPT-OSS 120B (open-weight) through the free Groq API (fast, no cost), temperature 0.1 for consistent answers.
- **System prompt:** role = "patient math tutor"; instruction "think step by step"; fixed output format: *Given → To find → Step 1..n → EXPRESSION → FINAL ANSWER*.
- **Few-shot example:** one solved problem (pens and notebooks) shows the exact format, which made the output reliable to parse.
- **Verification hook:** the model must output a single pure-arithmetic `EXPRESSION:` line. The app evaluates it with SymPy (input is first filtered to digits and `+ - * / ( ) .` so no unsafe code can run) and compares it with the `FINAL ANSWER` number (1% tolerance for rounding).

## 3. Implementation Procedure
1. Created a Groq API key and stored it in `.env` (git-ignored).
2. Tested the prompt with 6 sample problems and tuned the format.
3. `solver.py`: `build_messages()` → `call_llm()` → `parse_response()` (regex for steps / expression / answer) → `verify()` (SymPy).
4. `app.py` (FastAPI) serves `/api/solve`; `static/index.html` is a custom UI designed for low cognitive load: one big input, a numbered topic index (no blank-page anxiety), staged loader (Reading → Planning → Calculating → Verifying), and an exam-style answer sheet: Q. line, a Data / Required table, steps numbered in a red margin on ruled lines, the final answer boxed and double-underlined after a ∴ sign, and the SymPy result shown as a teacher's stamp (= checked / ≠ recheck). **Learn mode** reveals one step at a time and blurs the answer so students attempt each step first. Also added **dark mode** (eye comfort for night study) and a searchable **solve history** stored in the browser, so past solutions reopen instantly without another API call.
5. Pushed code to GitHub with README, requirements.txt and .gitignore.

## 4. Testing on Sample Inputs
| # | Problem (short) | Expected | LLM answer | SymPy check |
|---|---|---|---|---|
| 1 | Train 360 km in 4 h, time for 540 km | 6 h | 6 h | Pass |
| 2 | Riya = 3×Aman, total 64 | 48 | 48 marbles | Pass |
| 3 | Rs 800 shirt, 25% profit, SP | Rs 1000 | 1000 Rs | Pass |
| 4 | Rectangle, l = w+5, perimeter 50, area | 150 cm² | 150 cm² | Pass |
| 5 | Rs 10000 at 8% CI, 2 years | Rs 11664 | 11664 Rs | Pass |
| 6 | Pipes 6 h and 3 h together | 2 h | 2 hours | Pass |

**Result: 6/6 correct, all verified by SymPy.** Screenshots attached in `screenshots/`.

## 5. Results & Observations
- The step-by-step format made solutions easy to follow for students.
- The SymPy check catches cases where the explanation and final number disagree.
- Limitations: needs internet/API key; verification checks arithmetic, not whether the model chose the right equation; geometry diagrams / images are not supported.

## 6. Conclusion & Future Scope
A working LLM tutor that explains word problems and self-checks its arithmetic. Future work: Hindi/Marathi support, "hint mode" that reveals one step at a time, solving equations symbolically with SymPy `solve()`, and image input (photo of textbook problem).
