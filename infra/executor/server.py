import asyncio
import resource
import shutil
import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

JOBS_DIR = Path("/tmp/exec_jobs")
MAX_OUTPUT = 10_000
SEMAPHORE = asyncio.Semaphore(10)


class ExecuteRequest(BaseModel):
    source_code: str = Field(..., min_length=1, max_length=50_000)
    stdin: str = Field(default="", max_length=10_000)
    timeout_ms: int = Field(default=5_000, ge=100, le=10_000)


class ExecuteResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    signal: str | None
    runtime_ms: int
    timed_out: bool


def _apply_limits():
    resource.setrlimit(resource.RLIMIT_CPU, (12, 12))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024, 16 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))


async def _run(req: ExecuteRequest) -> ExecuteResponse:
    job_dir = JOBS_DIR / uuid4().hex
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "main.py").write_text(req.source_code, encoding="utf-8")

    try:
        async with SEMAPHORE:
            start = time.monotonic()
            proc = await asyncio.create_subprocess_exec(
                "python3",
                str(job_dir / "main.py"),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=job_dir,
                preexec_fn=_apply_limits,
            )
            try:
                out, err = await asyncio.wait_for(
                    proc.communicate(input=req.stdin.encode()),
                    timeout=req.timeout_ms / 1000,
                )
                return ExecuteResponse(
                    stdout=out.decode(errors="replace")[:MAX_OUTPUT],
                    stderr=err.decode(errors="replace")[:MAX_OUTPUT],
                    exit_code=proc.returncode or 0,
                    signal=None,
                    runtime_ms=int((time.monotonic() - start) * 1000),
                    timed_out=False,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return ExecuteResponse(
                    stdout="",
                    stderr="Time limit exceeded",
                    exit_code=124,
                    signal="SIGKILL",
                    runtime_ms=req.timeout_ms,
                    timed_out=True,
                )
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    assert shutil.which("python3"), "python3 not found"
    yield
    shutil.rmtree(JOBS_DIR, ignore_errors=True)


app = FastAPI(title="Code Executor", lifespan=lifespan)


@app.exception_handler(Exception)
async def _err(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal error"})


@app.post("/execute", response_model=ExecuteResponse)
async def execute(req: ExecuteRequest) -> ExecuteResponse:
    """Run python code"""
    return await _run(req)


@app.get("/health")
def health() -> dict:
    """Health check"""
    return {"status": "ok"}
