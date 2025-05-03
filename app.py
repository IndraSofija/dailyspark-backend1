from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
logger.info(f"API key is {'set' if api_key else 'not set'}")

# Create OpenAI client (correct for SDK 1.3.5)
client = OpenAI(api_key=api_key)

# Initialize FastAPI
app = FastAPI()

# Enable CORS
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
            messages=[{"role": "user", "content": prompt}]
        )
        generated_text = response.choices[0].message.content
        logger.info("Successfully received response from OpenAI")
        return {"result": generated_text}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"OpenAI API Error: {error_msg}")
        return {"error": f"Connection error: {error_msg}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port)
