from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

model = None
model_lock = asyncio.Lock()

class InferenceRequest(BaseModel):
    text: str

async def load_model():
    await asyncio.sleep(2)  # pretend it takes time
    return "Loaded AI Model"

@app.on_event("startup")
async def startup_event():
    global model
    async with model_lock:
        model = await load_model()
        print("Model loaded at startup")

@app.post("/predict")
async def predict(req: InferenceRequest):
    global model
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    # Optionally lock if accessing/updating shared state
    async with model_lock:
        # Simulate inference
        result = f"Prediction for '{req.text}' using {model}"
    
    return {"result": result}

