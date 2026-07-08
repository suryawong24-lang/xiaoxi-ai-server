import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import google.generativeai as genai

app = FastAPI()

# Konfigurasi API Key Gemini Gratisan Anda
GEMINI_API_KEY = "MASUKKAN_API_KEY_GEMINI_ANDA_DISINI"
genai.configure(api_key=GEMINI_API_KEY)

@app.get("/")
def home():
    return {"status": "Server Aktif", "info": "Server WebSocket AI untuk Xiaoxi Robot"}

# Endpoint WebSocket disesuaikan dengan ESP32 Anda: /api/v1/ws/chat
@app.websocket("/api/v1/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Robot Xiaoxi Terhubung via WebSocket!")
    
    try:
        while True:
            # Menerima data rekaman audio biner mentah dari ESP32
            audio_bytes = await websocket.receive_bytes()
            print(f"Menerima data suara sebesar {len(audio_bytes)} bytes dari robot.")
            
            try:
                # Memanggil Gemini AI menggunakan model gratisan paling stabil
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Pengkondisian awal: Karena data biner audio dari mic ESP32 butuh proses transkrip terpisah, 
                # Sementara kita trigger teks dulu untuk memastikan jalur komunikasi Railway <-> ESP32 tembus.
                prompt = "Halo Gemini, saya menerima data biner audio dari ESP32 Xiaoxi Robot. Berikan respon sapaan robot yang lucu dan singkat!"
                response = model.generate_content(prompt)
                
                # Kirim balik teks jawaban ke ESP32 via WebSocket
                await websocket.send_text(response.text)
                print(f"Respon dikirim ke robot: {response.text}")
                
            except Exception as e:
                await websocket.send_text(f"Error AI: {str(e)}")
                
    except WebSocketDisconnect:
        print("Robot Xiaoxi Terputus dari WebSocket.")