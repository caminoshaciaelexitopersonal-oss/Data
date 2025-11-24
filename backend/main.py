from fastapi import FastAPI
from backend.app_factory import create_app

# --- App Creation ---
# The app is now created and configured in the app_factory.
# We just import it. All other configurations, including agent setup,
# are now handled within their respective modules (e.g., agent/api.py)
# and routers.
app = create_app()

@app.get("/")
def read_root():
    return {"message": "SADI Backend is running."}

@app.get("/health", status_code=200)
def health_check():
    """Endpoint for health checks."""
    return {"status": "ok"}

# The following block is for running the app directly with uvicorn
# during development. It won't be executed when imported.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
