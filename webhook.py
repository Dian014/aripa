from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
from tenacity import retry, wait_fixed, stop_after_attempt
import socket
import time
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI()

class CallEvent(BaseModel):
    caller: constr(min_length=1, max_length=20)
    callee: constr(min_length=1, max_length=20)

@app.post("/incoming-call")
async def receive_call(event: CallEvent):
    logging.info("📞 Received call event from ACS:")
    logging.info(event.dict())

    try:
        send_sip_invite(event.caller, event.callee)
        logging.info("✅ SIP INVITE sent to Kamailio.")
        return {"status": "received"}
    except Exception as e:
        logging.error(f"❌ Failed to send SIP INVITE: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def send_sip_invite(caller: str, callee: str):
    kamailio_ip = "162.254.38.201"
    kamailio_port = 5060

    branch = str(int(time.time()))
    call_id = f"{branch}@python-client.local"

    # ✅ SDP Wajib agar 3CX terima call dan buka audio
    sdp = (
        "v=0\r\n"
        f"o=- 0 0 IN IP4 {kamailio_ip}\r\n"
        f"s=Python SIP Call\r\n"
        f"c=IN IP4 {kamailio_ip}\r\n"
        "t=0 0\r\n"
        "m=audio 4000 RTP/AVP 0 101\r\n"
        "a=rtpmap:0 PCMU/8000\r\n"
        "a=rtpmap:101 telephone-event/8000\r\n"
        "a=fmtp:101 0-15\r\n"
        "a=sendrecv\r\n"
    )

    content_length = len(sdp.encode())

    sip_message = (
        f"INVITE sip:{callee}@{kamailio_ip} SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP python-client.local;branch=z9hG4bK{branch}\r\n"
        f"Max-Forwards: 70\r\n"
        f"From: <sip:{caller}@python-client.local>;tag=12345\r\n"
        f"To: <sip:{callee}@{kamailio_ip}>\r\n"
        f"Call-ID: {call_id}\r\n"
        f"CSeq: 1 INVITE\r\n"
        f"Contact: <sip:{caller}@python-client.local>\r\n"
        f"User-Agent: Python-SIP-Client/1.0\r\n"
        f"Content-Type: application/sdp\r\n"
        f"Content-Length: {content_length}\r\n"
        f"\r\n"
        f"{sdp}"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(sip_message.encode(), (kamailio_ip, kamailio_port))
