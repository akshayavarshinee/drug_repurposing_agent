from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
import logging
from app.database import create_tables
from app.auth.routes import router as auth_router, get_current_user
from app.users.routes import router as users_router
from app.queries.routes import router as queries_router
from app.results.routes import router as results_router
from app.users.models import User

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    try:
        create_tables()
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    yield
    logger.info("Shutting down application...")

app = FastAPI(title="Drug Repurposing Platform", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(queries_router, prefix="/api/query", tags=["Queries"])
app.include_router(results_router, prefix="/api/results", tags=["Results"])

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """
    Landing page with sign in/create account button.
    """
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """
    User registration page.
    """
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    User login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/query", response_class=HTMLResponse)
async def query_page(request: Request, current_user: User = Depends(get_current_user)):
    """
    Query/chat page for authenticated users.
    """
    return templates.TemplateResponse("query.html", {
        "request": request,
        "user": current_user
    })

@app.get("/results/{report_id}", response_class=HTMLResponse)
async def results_page(request: Request, report_id: int, current_user: User = Depends(get_current_user)):
    """
    Results page showing generated report.
    """
    return templates.TemplateResponse("results.html", {
        "request": request,
        "report_id": report_id,
        "user": current_user
    })

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, current_user: User = Depends(get_current_user)):
    """
    History page showing all past reports.
    """
    return templates.TemplateResponse("history.html", {
        "request": request,
        "user": current_user
    })

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
