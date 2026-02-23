from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.solo_controller import router as solo_router
app = FastAPI(title="Agastya Solo × Senjyu-Light")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(solo_router, prefix="/api/solo", tags=["solo"])
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
