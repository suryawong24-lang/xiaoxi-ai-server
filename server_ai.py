import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

# 1. Inisialisasi FastAPI
app = FastAPI()

# 2. Konfigurasi API Key Gemini Anda (Gratis)
# Masukkan API Key Anda di dalam tanda kutip di bawah ini
GEMINI_API_KEY = "MASUKKAN_API_KEY_GEMINI_ANDA_DISINI"
genai.configure(api_key=GEMINI_API_KEY)

# Format data yang dikirim oleh ESP32 (Teks/Prompt)
class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"status": "Server Aktif", "info": "Server AI untuk ESP32"}

# End Point untuk menerima teks dari ESP32 dan menembak ke Gemini AI
@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Menggunakan model Gemini paling stabil
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Kirim teks dari ESP32 ke Gemini
        response = model.generate_content(request.message)
        
        # Kembalikan jawaban teks ke ESP32
        return {"response": response.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Untuk menjalankan server di laptop (lokal) saat pengetesan
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)