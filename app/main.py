from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.auth import router as auth_router
from app.api.items import router as items_router
from app.core.config import settings

app = FastAPI(title="DevSecOps API", version="0.1.0")

# Only allow common local hosts; adjust per environment
# Avoid * in production for greater security.
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

# CORS configuration; keep it tight in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    # Simple liveness route
    return {"status": "ok"}

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(items_router, prefix="/items", tags=["items"])