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
# Izveidot OpenAI klientu ar palielinātu taimautu
api_key = os.getenv("OPENAI_API_KEY")
logger.info(f"API key is {'set' if api_key else 'not set'}")

# Izveidot HTTP klientu ar palielinātu taimautu
http_client = httpx.Client(timeout=60.0)

# Izveidot OpenAI klientu ar pielāgotu HTTP klientu
client = OpenAI(
    api_key=api_key,
    http_client=http_client,
    timeout=60.0  # 60 sekundes taimauts
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

        # Mēģinām ar citu modeli, ja gpt-3.5-turbo nedarbojas
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                timeout=60  # 60 sekundes taimauts
            )
        except Exception as model_error:
            logger.warning(f"Error with gpt-3.5-turbo: {str(model_error)}. Trying text-davinci-003...")
            response = client.completions.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=500,
                timeout=60
            )
            generated_text = response.choices[0].text.strip()
            return {"result": generated_text}

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
