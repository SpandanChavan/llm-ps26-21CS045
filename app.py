"""Web app: FastAPI backend + hand-built HTML frontend (static/index.html).

Run:  python app.py   ->  open http://localhost:8000
"""
import os
import webbrowser

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from solver import MODEL, solve, structure

app = FastAPI(title="Math Word Problem Solver")
STATIC = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class Problem(BaseModel):
    problem: str


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC, "index.html"))


@app.get("/api/info")
def info():
    return {"model": MODEL}


@app.post("/api/solve")
def api_solve(body: Problem):
    text = body.problem.strip()
    if not text:
        raise HTTPException(400, "Please type a word problem first.")
    if len(text) > 2000:
        raise HTTPException(400, "Problem is too long (max 2000 characters).")
    try:
        r = solve(text)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"LLM call failed: {e}") from e
    return {**structure(r["steps"]), "final": r["final_text"], "expression": r["expression"],
            "verification": r["verification"], "raw": r["raw"]}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    if not os.getenv("NO_BROWSER"):
        webbrowser.open(f"http://localhost:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
