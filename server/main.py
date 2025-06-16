from pathlib import Path
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pymavlink import mavutil
import openai

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In‑memory session store: {session_id: {"history": [...], "file": path}}
SESSIONS = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

def parse_log(file_path: Path):
    """Placeholder for real MAVLink/DataFlash parsing."""
    # Load your parser here (e.g., pymavlink, dataflash library) and
    # extract telemetry info you want to feed to the LLM.
    return {"summary": "example telemetry data"}

@app.post("/")
async def upload_log(file: UploadFile = File(...)):
    """Accepts a .tlog file upload, parses it with pymavlink, and returns a session ID."""
    session_id = uuid.uuid4().hex
    dest = UPLOAD_DIR / f"{session_id}_{file.filename}"

    # Save uploaded file
    with dest.open("wb") as f:
        f.write(await file.read())

    # Parse the .tlog file using pymavlink
    try:
        print(f"\n📦 Parsing {dest.name}...\n")
        mav = mavutil.mavlink_connection(str(dest))
        count = 0

        while True:
            msg = mav.recv_match(blocking=False)
            if msg is None:
                break
            print(msg)
            count += 1
            if count >= 20:  # Limit to first 20 messages for preview
                print(f"...({count} messages printed)")
                break
    except Exception as e:
        print(f"❌ Error parsing file: {e}")

    # Store session info
    SESSIONS[session_id] = {"history": [], "file": dest}

    return {"session_id": session_id}

@app.get("/uploaded/{session_id}")
def get_uploaded_file(session_id: str):
    session = SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return FileResponse(path=session["file"], filename=session["file"].name)

@app.post("/api/chat")
async def chat(req: ChatRequest):
    session = SESSIONS.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    telemetry = parse_log(session["file"])
    # Compose the prompt with conversation history + new user message
    history = session["history"]
    messages = [{"role": "system", "content": "You are a UAV log analysis assistant."}]
    for h in history:
        messages.append(h)
    messages.append({"role": "user", "content": req.message})
    # Inject telemetry info
    messages.append({"role": "system", "content": f"Telemetry summary: {telemetry}"})

    # Call your LLM (OpenAI, Anthropic, etc.)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    answer = response["choices"][0]["message"]["content"]

    # Update conversation history
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": answer})

    return {"answer": answer}
