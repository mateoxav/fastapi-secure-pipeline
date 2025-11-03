from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.auth import router as auth_router
from app.api.items import router as items_router
from app.core.config import settings 

app = FastAPI(title=settings.project_name, version="1.0.0")

# PRODUCTION-READY MIDDLEWARE CONFIGURATION
# This application follows security best practices by being secure by default
# and loading its configuration from the environment (via the settings module).
# This avoids hardcoding development settings like ["*"] into the codebase.

# Protect against Host Header attacks
# Loads the list of allowed hosts directly from settings
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts
)

# Configure Cross-Origin Resource Sharing (CORS)
# Loads the list of allowed origins directly from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)


# STATIC FILES SERVING
# Mounts the 'web' directory to serve static files (HTML, CSS, JS)
# This allows the frontend to be served directly from the same application.
# Files in the 'web' folder are accessible via the "/static" URL path.
app.mount("/static", StaticFiles(directory="web"), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """
    Serves the main index.html file as the root of the application.
    This allows users to navigate directly to http://localhost:8000 to see the frontend.
    """
    return FileResponse('web/index.html')


@app.get("/health", tags=["Health"])
def health():
    """
    Simple liveness probe endpoint to check if the application is running.
    """
    return {"status": "ok"}


# --- API ROUTERS ---
# Include the API endpoints for authentication and items.
# These are the core business logic of the application.
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(items_router, prefix="/items", tags=["Items"])
