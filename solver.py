"""Core logic: build prompt -> call LLM -> parse answer -> verify arithmetic with SymPy."""
import os
import re

import sympy
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = """You are a patient math tutor for school and college students.
Solve the word problem the student gives you. Think step by step.

Follow this exact format:

**Given:** list the known quantities with units.
**To find:** what the question asks.

**Step 1:** <what you do and why> -> <calculation> = <result>
**Step 2:** ...
(use as many steps as needed; one operation idea per step, explained in simple words)

EXPRESSION: <one single Python arithmetic expression, using only numbers, + - * / ** and parentheses, that computes the final numeric answer directly from the given numbers>
FINAL ANSWER: <number> <unit>

Rules:
- EXPRESSION and FINAL ANSWER must be the last two lines.
- In EXPRESSION, do not use variables, words, units, % signs or commas inside numbers.
- If the problem has no numeric answer, write EXPRESSION: none.
- Write plain text only. Do NOT use LaTeX or backslash commands. Use * or x for multiply and / for divide.
"""

FEW_SHOT_USER = "A pen costs Rs 12 and a notebook costs Rs 35. How much do 3 pens and 2 notebooks cost?"
FEW_SHOT_ASSISTANT = """**Given:** pen = Rs 12, notebook = Rs 35, buying 3 pens and 2 notebooks.
**To find:** total cost.

**Step 1:** Cost of 3 pens -> 3 * 12 = 36
**Step 2:** Cost of 2 notebooks -> 2 * 35 = 70
**Step 3:** Add both costs -> 36 + 70 = 106

EXPRESSION: 3*12 + 2*35
FINAL ANSWER: 106 Rs"""


def build_messages(problem: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": FEW_SHOT_USER},
        {"role": "assistant", "content": FEW_SHOT_ASSISTANT},
        {"role": "user", "content": problem.strip()},
    ]


def call_llm(problem: str, api_key: str | None = None, temperature: float = 0.1) -> str:
    from groq import Groq

    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("No GROQ_API_KEY found. Put it in a .env file or paste it in the sidebar.")
    client = Groq(api_key=key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=build_messages(problem),
        temperature=temperature,
    )
    return resp.choices[0].message.content


_NUM = re.compile(r"-?\d[\d,]*\.?\d*(?:/\d+)?")


def parse_response(text: str) -> dict:
    """Split the LLM output into steps, expression and final answer."""
    expr = re.search(r"^\s*EXPRESSION:\s*(.+)$", text, re.M | re.I)
    final = re.search(r"^\s*\**FINAL ANSWER:?\**:?\s*(.+)$", text, re.M | re.I)
    steps = re.split(r"^\s*EXPRESSION:", text, flags=re.M | re.I)[0].strip()
    final_text = final.group(1).strip() if final else ""
    num = _NUM.search(final_text)
    return {
        "steps": steps,
        "expression": expr.group(1).strip().strip("`") if expr else None,
        "final_text": final_text,
        "final_number": num.group(0).replace(",", "") if num else None,
    }


_SAFE_EXPR = re.compile(r"^[\d\s+\-*/().]+$")


def verify(expression: str | None, final_number: str | None) -> dict:
    """Recompute the expression with SymPy and compare with the stated answer."""
    if not expression or expression.lower() == "none":
        return {"status": "skipped", "message": "No arithmetic expression to check."}
    if not _SAFE_EXPR.match(expression):
        return {"status": "skipped", "message": f"Expression not purely numeric: `{expression}`"}
    try:
        value = sympy.sympify(expression, rational=True)
        computed = float(value)
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"Could not evaluate expression: {e}"}
    if final_number is None:
        return {"status": "skipped", "computed": computed, "message": "No numeric final answer found."}
    try:
        stated = float(sympy.sympify(final_number, rational=True))
    except Exception:  # noqa: BLE001
        return {"status": "skipped", "computed": computed, "message": "Could not read final answer."}
    ok = abs(computed - stated) <= max(1e-6, 0.01 * abs(computed))  # 1% tolerance for rounding
    return {
        "status": "pass" if ok else "fail",
        "computed": computed,
        "stated": stated,
        "message": "Arithmetic verified by SymPy." if ok else "Mismatch between steps and final answer!",
    }


def solve(problem: str, api_key: str | None = None) -> dict:
    raw = call_llm(problem, api_key)
    parsed = parse_response(raw)
    parsed["verification"] = verify(parsed["expression"], parsed["final_number"])
    parsed["raw"] = raw
    return parsed


_STEP = re.compile(r"^\s*\**Step\s*(\d+)\s*:?\**:?\s*(.+)$", re.I)
_FIELD = re.compile(r"^\s*\**(Given|To find)\s*:?\**:?\s*(.+)$", re.I)


def structure(steps_text: str) -> dict:
    """Turn the markdown steps into {given, to_find, steps:[{n, explain, calc}]} for the web UI."""
    out = {"given": "", "to_find": "", "steps": []}
    field = None
    for line in steps_text.splitlines():
        if m := re.match(r"^\s*\**(Given|To find)\s*:?\**:?\s*(.*)$", line, re.I):
            field = "given" if m.group(1).lower() == "given" else "to_find"
            out[field] = m.group(2).strip()
        elif field and not out["steps"] and re.match(r"^\s*[-*•]\s+", line):
            item = re.sub(r"^\s*[-*•]\s+", "", line).strip()
            out[field] = f"{out[field]}; {item}".strip("; ") if out[field] else item
        elif m := _STEP.match(line):
            field = None
            body = m.group(2).strip()
            explain, _, calc = body.partition("->") if "->" in body else body.partition("→")
            out["steps"].append({"n": int(m.group(1)), "explain": explain.strip(), "calc": calc.strip()})
        elif out["steps"] and line.strip() and not line.strip().startswith("**"):
            out["steps"][-1]["explain"] += " " + line.strip()
    return out
