from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_roo():
    return {"hello world"}
