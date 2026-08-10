from fastapi import FastAPI

from api.routes import router


app = FastAPI(
    title="Startup Investment Research API",
    version="1.0.0",
    description="AI-powered startup investment research system",
)


app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }