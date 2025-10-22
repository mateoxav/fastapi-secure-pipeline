from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.auth import router as auth_router
from app.api.items import router as items_router
from app.core.config import settings

app = FastAPI(title=settings.project_name, version="1.0.0")

# Add TrustedHostMiddleware to protect against Host header attacks
# In production, you should be more restrictive, e.g., ["your-domain.com"]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

# CORS configuration, keep it tight in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health():
    # Simple liveness route
    return {"status": "ok"}

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(items_router, prefix="/items", tags=["Items"])