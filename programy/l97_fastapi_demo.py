"""Lekce 97 — FastAPI demo.

Spuštění:
    pip install "fastapi[standard]"
    fastapi dev l97_fastapi_demo.py
    → http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(title="Mini API")


class Pes(BaseModel):
    jmeno: str = Field(min_length=1, max_length=30)
    vek: int = Field(ge=0, le=30)


PSI: dict[int, Pes] = {}
DALSI_ID = 1


@app.get("/")
def root() -> dict:
    return {"zprava": "Vítej v psí evidenci 🐕"}


@app.get("/psi")
def list_psi() -> list[dict]:
    return [{"id": i, **p.model_dump()} for i, p in PSI.items()]


@app.post("/psi", status_code=201)
def vytvor(pes: Pes) -> dict:
    global DALSI_ID
    PSI[DALSI_ID] = pes
    odpoved = {"id": DALSI_ID, **pes.model_dump()}
    DALSI_ID += 1
    return odpoved


@app.get("/psi/{id}")
def get_pes(id: int) -> dict:
    if id not in PSI:
        raise HTTPException(404, "Pes nenalezen")
    return {"id": id, **PSI[id].model_dump()}


@app.delete("/psi/{id}", status_code=204)
def smaz(id: int) -> None:
    PSI.pop(id, None)
