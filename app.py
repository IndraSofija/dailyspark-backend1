from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

# Ielādē .env failu (Railway vidē tas ir optional, bet lokālai testēšanai noder)
load_dotenv()

# Iestata žurnālošanu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializē OpenAI klientu
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicializē FastAPI
app = FastAPI()

# Atļauj CORS no jebkuras izcelsmes (attīstības posmā noderīgi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Saknes maršruts - pārbaudei
@app.get("/")
async def root():
    return {"message": "DailySpark backend is running."}

# Ģenerēšanas API maršruts
@app.post("/generate")
async def generate_content(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content.strip()
        return {"result": result}
    except Exception as e:
        logger.error(f"Kļūda ģenerēšanā: {e}")
        return {"error": str(e)}
