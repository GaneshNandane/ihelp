from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_settings
from backend.routes import (
    auth,
    industry,
    institute,
    jobs,
    skills,
    students,
    technologies,
    updates,
)


settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"
RESUMES_DIR = BASE_DIR / "data" / "resumes"
RESUMES_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Routers
app.include_router(jobs.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(students.router, prefix=settings.api_prefix)
app.include_router(institute.router, prefix=settings.api_prefix)
app.include_router(industry.router, prefix=settings.api_prefix)
app.include_router(skills.router, prefix=settings.api_prefix)
app.include_router(technologies.router, prefix=settings.api_prefix)
app.include_router(updates.router, prefix=settings.api_prefix)

# Mount resumes static file serving
app.mount("/resumes", StaticFiles(directory=RESUMES_DIR), name="resumes")


@app.get("/", response_model=None)
def root() -> FileResponse | dict[str, str]:
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    return {"status": "ok", "service": settings.app_name}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


if FRONTEND_DIST.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )


@app.get("/{path:path}", include_in_schema=False)
def serve_frontend(path: str) -> FileResponse:
    if not FRONTEND_DIST.exists():
        raise HTTPException(status_code=404, detail="Frontend build not found.")

    index_file = FRONTEND_DIST / "index.html"
    requested_file = FRONTEND_DIST / path

    if requested_file.is_file():
        return FileResponse(requested_file)

    return FileResponse(index_file)
