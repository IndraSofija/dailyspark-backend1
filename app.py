from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import httpx

# Iestatīt žurnalēšanu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
# Izveidot OpenAI klientu ar timeout iestatījumiem
api_key = os.getenv("OPENAI_API_KEY")
logger.info(f"API key is {'set' if api_key else 'not set'}")

# Izveidot klientu ar timeout iestatījumiem
client = OpenAI(
    api_key=api_key,
    timeout=httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "DailySpark backend is running."}

@app.post("/generate")
async def generate_text(request: Request):
    body = await request.json()
    prompt = body.get("prompt")

    if not prompt:
        return {"error": "No prompt provided."}

    try:
        logger.info(f"Sending request to OpenAI with prompt: {prompt[:50]}...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=45.0  # Papildu timeout šim konkrētajam pieprasījumam
        )
        generated_text = response.choices[0].message.content
        logger.info("Successfully received response from OpenAI")
        return {"result": generated_text}
    except httpx.TimeoutException as e:
        error_msg = str(e)
        logger.error(f"OpenAI API Timeout: {error_msg}")
        return {"error": f"Connection timeout: {error_msg}"}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"OpenAI API Error: {error_msg}")
        return {"error": f"Connection error: {error_msg}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port)
