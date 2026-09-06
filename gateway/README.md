# Digi-Chalk Local Gateway Service

This is the offline-first classroom gateway that runs locally (e.g. on a Raspberry Pi or Teacher's laptop). It captures sensor data (currently simulated), broadcasts strokes to local devices via WebSockets, and syncs to the cloud backend when internet is available.

## Installation (Windows PowerShell)

```powershell
cd gateway
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the Gateway

Start the FastAPI server:
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8001
```
The gateway will start on `http://127.0.0.1:8001`.

## Local Frontend Integration

To connect the frontend to the gateway instead of the cloud backend:
1. Open the browser dev tools (F12) on the Digi-Chalk frontend.
2. Run `localStorage.setItem("GATEWAY_URL", "http://127.0.0.1:8001")`
3. Refresh the page. 
Now, "Start Session" and WebSocket board strokes will be routed through the local Gateway.

## Simulated Hardware / Offline Sync

- **Strokes:** Use the teacher frontend to draw, or POST to `/simulate/stroke/`.
- **Bookmarks:** Click the bookmark button in the frontend or POST to `/sessions/{id}/bookmarks/`.
- **Sync:** When connected to the internet, call `POST /sync/now/` to push all offline events to the Django backend.
- **Hardware Integration:** Real BLE (Bluetooth) and UDP TDOA integration are deferred to Phase 4. `app/adapters/sensor.py` provides the interfaces.
