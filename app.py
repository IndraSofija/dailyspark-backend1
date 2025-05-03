from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import httpx
import time
import socket

# Iestatīt žurnalēšanu ar detalizētāku formātu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("app")

# Ielādēt vides mainīgos
load_dotenv()

# Izveidot OpenAI klientu ar timeout iestatījumiem
api_key = os.getenv("OPENAI_API_KEY")
logger.info(f"API key is {'set' if api_key else 'not set'}")

# Izveidot klientu ar timeout iestatījumiem
client = OpenAI(
    api_key=api_key,
    timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0)
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
    try:
        body = await request.json()
        prompt = body.get("prompt")

        if not prompt:
            logger.warning("No prompt provided in request")
            return {"error": "No prompt provided."}

        logger.info(f"Sending request to OpenAI with prompt: {prompt[:50]}...")

        # Pārbaudīt tīkla savienojumu pirms pieprasījuma
        try:
            # Mēģināt izveidot savienojumu ar OpenAI API
            socket.create_connection(("api.openai.com", 443), timeout=5)
            logger.info("Network connection to OpenAI API is available")
        except (socket.timeout, socket.error) as e:
            logger.error(f"Network connectivity issue: {str(e)}")
            return {"error": f"Network connectivity issue: {str(e)}"}

        # Mērīt pieprasījuma laiku
        start_time = time.time()

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                timeout=45.0  # Papildu timeout šim konkrētajam pieprasījumam
            )

            elapsed_time = time.time() - start_time
            logger.info(f"OpenAI API response received in {elapsed_time:.2f} seconds")

            generated_text = response.choices[0].message.content
            logger.info("Successfully received response from OpenAI")
            return {"result": generated_text}

        except httpx.TimeoutException as e:
            elapsed_time = time.time() - start_time
            logger.error(f"OpenAI API Timeout after {elapsed_time:.2f} seconds: {str(e)}")
            return {"error": f"Connection timeout after {elapsed_time:.2f} seconds. The OpenAI API took too long to respond."}

        except httpx.ConnectError as e:
            logger.error(f"OpenAI API Connection Error: {str(e)}")
            return {"error": f"Connection error: Could not connect to OpenAI API. Please check your network connection and API key."}

        except httpx.RequestError as e:
            logger.error(f"OpenAI API Request Error: {str(e)}")
            return {"error": f"Request error: {str(e)}"}

        except Exception as e:
            logger.error(f"OpenAI API Error: {str(e)}", exc_info=True)
            return {"error": f"Connection error: {str(e)}"}

    except Exception as e:
        logger.error(f"Request processing error: {str(e)}", exc_info=True)
        return {"error": f"Error processing request: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port)
