import subprocess
import tempfile
import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Code Executor")

MAX_TIMEOUT = 10
MAX_OUTPUT  = 10_000


class ExecuteRequest(BaseModel):
    source_code: str
    stdin: str = ""
    timeout_ms: int = 5000


class ExecuteResponse(BaseModel):
    stdout:     str
    stderr:     str
    exit_code:  int
    runtime_ms: int
    timed_out:  bool


@app.post("/execute", response_model=ExecuteResponse)
def execute(req: ExecuteRequest):
    if not req.source_code:
        raise HTTPException(status_code=400, detail="No source_code provided")

    timeout_secs = min(req.timeout_ms, MAX_TIMEOUT * 1000) / 1000

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="/tmp"
    ) as f:
        f.write(req.source_code)
        tmp_path = f.name

    try:
        start = time.monotonic()
        result = subprocess.run(
            ["python", tmp_path],
            input=req.stdin,
            capture_output=True,
            text=True,
            timeout=timeout_secs,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)

        return ExecuteResponse(
            stdout=result.stdout[:MAX_OUTPUT],
            stderr=result.stderr[:MAX_OUTPUT],
            exit_code=result.returncode,
            runtime_ms=elapsed_ms,
            timed_out=False,
        )

    except subprocess.TimeoutExpired:
        return ExecuteResponse(
            stdout="",
            stderr="Time limit exceeded",
            exit_code=124,
            runtime_ms=req.timeout_ms,
            timed_out=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@app.get("/health")
def health():
    return {"status": "ok"}
