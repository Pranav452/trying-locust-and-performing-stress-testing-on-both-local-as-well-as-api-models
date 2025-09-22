import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from openai import OpenAI
from dotenv import load_dotenv
import requests
from prometheus_client import make_asgi_app
import tiktoken
from metrics import record_request, set_active_requests

load_dotenv()

app = FastAPI(title="llm api", version="1.0.0")

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

MODEL_BACKEND = os.getenv("MODEL_BACKEND", "ollama")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class GenRequest(BaseModel):
    prompt: str
    max_tokens: int = 128
    temperature: float = 0.8
    user_id: str = "anonymous"

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken"""
    try:
        if model.startswith("gpt"):
            encoding = tiktoken.encoding_for_model("gpt-4")
        else:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimation
        return len(text.split()) * 1.3


@app.get("/")
def root():
    return {"message": "Hello World", "model_backend": MODEL_BACKEND}


@app.get("/health")
async def health():
    return {"message": "OK"}

async def _generate_ollama(req: GenRequest):
    payload ={
        "model":"tinyllama",
        "prompt":req.prompt,
        "options":{
            "temperature":req.temperature,
            "max_tokens":req.max_tokens,
        },
        "stream":False,

    }
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # First check if Ollama server is reachable
        health_response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if health_response.status_code != 200:
            raise HTTPException(status_code=503, detail="Ollama server is not reachable")
            
        response = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=120)
        
        # Check for specific Ollama errors
        if response.status_code != 200:
            error_detail = f"Ollama API error: {response.status_code} - {response.text}"
            raise HTTPException(status_code=500, detail=error_detail)
            
        result = response.json()
        
        # Check if there's an error in the response
        if "error" in result:
            error_detail = f"Ollama model error: {result['error']}"
            raise HTTPException(status_code=500, detail=error_detail)
            
        text = result.get("response","")
        return {
            "text":text,
            "token_used":0,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def _generate_openai(req: GenRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set")
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": req.prompt}],
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )
       
        text = response.choices[0].message.content
        token_used = getattr(response.usage, "total_tokens", 0)
        return {
            "text": text,
            "token_used": token_used,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#factory pattern
@app.post("/generate")
async def generate(req: GenRequest):
    start_time = time.time()
    model_name = "gpt-4.1-nano" if MODEL_BACKEND == "openai" else "tinyllama"
    
    # Count active requests
    set_active_requests(MODEL_BACKEND, model_name, 1)
    
    try:
        if MODEL_BACKEND == "openai":
            result = await _generate_openai(req)
        elif MODEL_BACKEND == "ollama":
            result = await _generate_ollama(req)
        else:
            raise HTTPException(status_code=400, detail="Model backend not supported")
        
        # Calculate metrics
        latency = time.time() - start_time
        tokens_in = int(count_tokens(req.prompt, model_name))
        tokens_out = int(count_tokens(result.get("text", ""), model_name))
        
        # Record metrics
        record_request(
            backend=MODEL_BACKEND,
            user=req.user_id,
            model=model_name,
            status="success",
            latency=latency,
            tokens_in=tokens_in,
            tokens_out=tokens_out
        )
        
        # Update result with actual token counts
        result["token_used"] = tokens_in + tokens_out
        result["tokens_in"] = tokens_in
        result["tokens_out"] = tokens_out
        result["latency"] = latency
        
        return result
        
    except HTTPException as e:
        # Record failed request
        latency = time.time() - start_time
        tokens_in = int(count_tokens(req.prompt, model_name))
        
        record_request(
            backend=MODEL_BACKEND,
            user=req.user_id,
            model=model_name,
            status="error",
            latency=latency,
            tokens_in=tokens_in,
            tokens_out=0
        )
        raise e
    finally:
        # Reset active requests
        set_active_requests(MODEL_BACKEND, model_name, 0)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)