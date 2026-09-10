from fastapi import FastAPI

app = FastAPI(title="FactCheck AI API")

@app.get("/")
def read_root():
    return {"message": "Welcome to FactCheck AI Backend", "status": "Active"}
