from fastapi import FastAPI
import os

from .router import router as voice_router


app = FastAPI(title="Voice Agent API", version="0.1.0")
app.include_router(voice_router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8100"))
    uvicorn.run(app, host="0.0.0.0", port=port)


