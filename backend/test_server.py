from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/test")
def test():
    return {"message": "FastAPI is working!"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "fastapi"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3001, log_level="info")