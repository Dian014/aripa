from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}  # fallback ke data kosong

    print("📥 Payload diterima:", data)
    return {"message": "Webhook diterima", "data": data}
