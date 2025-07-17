from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    print("📩 Webhook diterima:", data)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("webhook:app", host="0.0.0.0", port=8000)
