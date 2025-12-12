"""
LAN Audio Streamer - Server
Streams Windows system audio over LAN using WASAPI loopback capture.
Uses PyAudioWPatch for proper WASAPI loopback support.
"""

import asyncio
import json
import sys
import threading
from collections import deque
from pathlib import Path
from typing import Set

import numpy as np

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    print("Error: PyAudioWPatch not found. Install it with: pip install PyAudioWPatch")
    sys.exit(1)

try:
    from aiohttp import web, WSMsgType
except ImportError:
    print("Error: aiohttp module not found. Install it with: pip install aiohttp")
    sys.exit(1)


# Configuration
SAMPLE_RATE = 48000
CHANNELS = 2
CHUNK_SIZE = 1920  # ~20ms chunks at 48kHz for low latency
BUFFER_CHUNKS = 2  # Buffer chunks
PORT = 8765


class AudioCapture:
    """Captures system audio using WASAPI loopback."""
    
    def __init__(self):
        self.running = False
        self.clients: Set[web.WebSocketResponse] = set()
        self.lock = threading.Lock()
        self.audio_buffer = deque(maxlen=BUFFER_CHUNKS)
        self.capture_thread = None
        self.p = None
        self.stream = None
        self.device_sample_rate = SAMPLE_RATE
        self.device_channels = CHANNELS
        
    def get_loopback_device(self, p):
        """Get the WASAPI loopback device for capturing system audio."""
        try:
            # Get default WASAPI output device info
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            print(f"Default output device: {default_speakers['name']}")
            
            # Check if it's a loopback device
            if not default_speakers.get("isLoopbackDevice", False):
                # Find the loopback device for this output
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        print(f"Found loopback device: {loopback['name']}")
                        return loopback
                
                # If no matching loopback found, use first available loopback
                for loopback in p.get_loopback_device_info_generator():
                    print(f"Using loopback device: {loopback['name']}")
                    return loopback
            else:
                return default_speakers
                
        except Exception as e:
            print(f"Error finding loopback device: {e}")
            # Try to find any loopback device
            try:
                for loopback in p.get_loopback_device_info_generator():
                    print(f"Fallback loopback device: {loopback['name']}")
                    return loopback
            except Exception as e2:
                print(f"No loopback devices found: {e2}")
        
        return None
    
    def capture_loop(self, loop):
        """Main audio capture loop running in a separate thread."""
        self.p = pyaudio.PyAudio()
        
        device = self.get_loopback_device(self.p)
        if not device:
            print("No loopback device found!")
            print("\nAvailable devices:")
            for i in range(self.p.get_device_count()):
                dev = self.p.get_device_info_by_index(i)
                print(f"  [{i}] {dev['name']} (in: {dev['maxInputChannels']}, out: {dev['maxOutputChannels']})")
            self.p.terminate()
            return
        
        # Use the device's native sample rate and channels
        self.device_sample_rate = int(device["defaultSampleRate"])
        self.device_channels = device["maxInputChannels"]
        
        print(f"Device sample rate: {self.device_sample_rate}Hz, channels: {self.device_channels}")
        
        try:
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=self.device_channels,
                rate=self.device_sample_rate,
                input=True,
                input_device_index=device["index"],
                frames_per_buffer=CHUNK_SIZE
            )
            
            print(f"Audio capture started at {self.device_sample_rate}Hz, {self.device_channels} channels")
            
            while self.running:
                try:
                    # Read audio data
                    audio_bytes = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    
                    # Add to buffer
                    self.audio_buffer.append(audio_bytes)
                    
                    # Send to all connected clients
                    with self.lock:
                        if self.clients:
                            # Schedule sending to clients from the event loop
                            asyncio.run_coroutine_threadsafe(
                                self.broadcast(audio_bytes),
                                loop
                            )
                except Exception as e:
                    if self.running:
                        print(f"Capture error: {e}")
                        
        except Exception as e:
            print(f"Failed to start audio capture: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.p:
                self.p.terminate()
    
    async def broadcast(self, audio_bytes: bytes):
        """Send audio data to all connected WebSocket clients."""
        disconnected = set()
        
        with self.lock:
            clients = list(self.clients)
        
        for client in clients:
            try:
                if not client.closed:
                    await client.send_bytes(audio_bytes)
            except Exception:
                disconnected.add(client)
        
        # Remove disconnected clients
        if disconnected:
            with self.lock:
                self.clients -= disconnected
            print(f"Removed {len(disconnected)} disconnected client(s)")
    
    def start(self, loop):
        """Start the audio capture thread."""
        if not self.running:
            self.running = True
            self.capture_thread = threading.Thread(
                target=self.capture_loop,
                args=(loop,),
                daemon=True
            )
            self.capture_thread.start()
    
    def stop(self):
        """Stop the audio capture."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
    
    def add_client(self, ws: web.WebSocketResponse):
        """Add a new WebSocket client."""
        with self.lock:
            self.clients.add(ws)
        print(f"Client connected. Total clients: {len(self.clients)}")
    
    def remove_client(self, ws: web.WebSocketResponse):
        """Remove a WebSocket client."""
        with self.lock:
            self.clients.discard(ws)
        print(f"Client disconnected. Total clients: {len(self.clients)}")


# Global audio capture instance
audio_capture = AudioCapture()


async def websocket_handler(request):
    """Handle WebSocket connections for audio streaming."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # Send configuration to client
    config = {
        "type": "config",
        "sampleRate": audio_capture.device_sample_rate,
        "channels": audio_capture.device_channels,
        "chunkSize": CHUNK_SIZE
    }
    await ws.send_str(json.dumps(config))
    
    # Add client to the broadcast list
    audio_capture.add_client(ws)
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                # Handle client messages (e.g., volume control, pause/play)
                try:
                    data = json.loads(msg.data)
                    if data.get("type") == "ping":
                        await ws.send_str(json.dumps({"type": "pong"}))
                except json.JSONDecodeError:
                    pass
            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")
    finally:
        audio_capture.remove_client(ws)
    
    return ws


async def index_handler(request):
    """Serve the main HTML page."""
    html_path = Path(__file__).parent / "static" / "index.html"
    return web.FileResponse(html_path)


async def static_handler(request):
    """Serve static files."""
    filename = request.match_info.get("filename", "index.html")
    static_path = Path(__file__).parent / "static" / filename
    if static_path.exists():
        return web.FileResponse(static_path)
    return web.Response(status=404, text="Not Found")


async def status_handler(request):
    """Return server status."""
    return web.json_response({
        "status": "running",
        "clients": len(audio_capture.clients),
        "sampleRate": audio_capture.device_sample_rate,
        "channels": audio_capture.device_channels
    })


def get_local_ip():
    """Get the local IP address for LAN access."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


async def on_startup(app):
    """Start audio capture when server starts."""
    loop = asyncio.get_event_loop()
    audio_capture.start(loop)


async def on_cleanup(app):
    """Stop audio capture when server shuts down."""
    audio_capture.stop()


def main():
    """Main entry point."""
    app = web.Application()
    
    # Routes
    app.router.add_get("/", index_handler)
    app.router.add_get("/ws", websocket_handler)
    app.router.add_get("/status", status_handler)
    app.router.add_get("/static/{filename}", static_handler)
    app.router.add_static("/static/", Path(__file__).parent / "static")
    
    # Lifecycle hooks
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    
    local_ip = get_local_ip()
    
    print("\n" + "=" * 60)
    print("  🎵 LAN Audio Streamer")
    print("=" * 60)
    print(f"\n  Server running at:")
    print(f"    • Local:   http://localhost:{PORT}")
    print(f"    • Network: http://{local_ip}:{PORT}")
    print(f"\n  Open the URL on any device on your network to listen!")
    print(f"\n  Press Ctrl+C to stop the server.")
    print("=" * 60 + "\n")
    
    web.run_app(app, host="0.0.0.0", port=PORT, print=None)


if __name__ == "__main__":
    main()
