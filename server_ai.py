from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import google.generativeai as genai
from gtts import gTTS
import os
import uvicorn

app = FastAPI()

# Masukkan API Key Gemini Anda di sini
GEMINI_API_KEY = "AIzaSyDwKTOZYk02y5ZAUvfvrAXAQcwpuHGLgf4"
genai.configure(api_key=GEMINI_API_KEY)

@app.websocket("/api/v1/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[SERVER]: Jalur WebSocket terbuka, siap melayani robot!")
    audio_buffer = bytearray()
    
    try:
        while True:
            # Terima data biner audio dari ESP32
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)
            
            # Jika buffer sudah cukup untuk durasi 7 detik (mengatur waktu rekaman)
            if len(audio_buffer) >= (16000 * 2 * 7):
                print("[PROSES]: Mengirim rekaman ke Gemini AI...")
                temp_in = "input_mic.wav"
                with open(temp_in, "wb") as f:
                    f.write(audio_buffer)
                
                # Kirim ke Gemini
                model = genai.GenerativeModel("gemini-1.5-flash")
                audio_file = genai.upload_file(path=temp_in)
                response = model.generate_content([
                    "Kamu adalah asisten pintar. Jawab dengan ramah, singkat, maksimal 1 kalimat pendek bahasa Indonesia:", 
                    audio_file
                ])
                
                # Proses Text-to-Speech (TTS)
                jawaban_teks = response.text.strip()
                print(f"[GEMINI]: {jawaban_teks}")
                
                tts = gTTS(text=jawaban_teks, lang='id')
                temp_out = "output_balasan.mp3"
                tts.save(temp_out)
                
                # Kirim balik audio ke ESP32
                with open(temp_out, "rb") as f:
                    await websocket.send_bytes(f.read())
                
                # Bersihkan
                os.remove(temp_in)
                os.remove(temp_out)
                audio_buffer.clear()
                
    except WebSocketDisconnect:
        print("[SERVER]: Robot terputus.")
    except Exception as e:
        print(f"[ERROR]: {str(e)}")
        await websocket.close()

if __name__ == "__main__":
    # Ini untuk menjalankan server di cloud nanti
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)