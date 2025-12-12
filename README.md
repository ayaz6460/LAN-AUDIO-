# 🎵 LAN Audio Streamer

Stream your Windows system audio over LAN to any device via browser. No apps. No drivers. WASAPI loopback.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **Real-time PC audio streaming** to your phone, tablet, or another PC
- **Browser-based**: Works instantly inside any modern browser (WebAudio + WebSocket)
- **Zero-installation on Client**: Just open a web page!
- **WASAPI Loopback**: Captures system audio output directly from the sound card
- **Multi-Client Streaming**: Stream to multiple devices simultaneously
- **Beautiful UI**: Clean, responsive player interface with visualizer
- **Robust Connection**: Auto-reconnect and queue buffering
- **Low Latency**: Optimized for real-time streaming

## 📋 Requirements

- Windows 10/11
- Python 3.8+
- Audio output device (speakers/headphones)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd lan-audio-stream
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python server.py
```

### 3. Connect from Any Device

Open the displayed URL in any browser on your network:
- Local: `http://localhost:8765`
- Network: `http://YOUR_IP:8765`

## 📱 Usage

1. **Start the server** on your Windows PC
2. **Open the URL** on your phone, tablet, or any device on the same network
3. **Click Play** to start streaming
4. **Adjust volume** using the slider
5. Enjoy your PC audio anywhere!

## 🔧 Configuration

Edit `server.py` to change settings:

```python
SAMPLE_RATE = 48000   # Audio sample rate (Hz)
CHANNELS = 2          # Stereo
CHUNK_SIZE = 1024     # Samples per chunk
PORT = 8765           # Server port
```

## 🛡️ Firewall

If clients can't connect, you may need to allow the port through Windows Firewall:

```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="LAN Audio Stream" dir=in action=allow protocol=tcp localport=8765
```

## 🎨 Screenshots

The web player features:
- Real-time audio visualizer
- Connection status indicator
- Volume control with smooth slider
- Latency and buffer monitoring
- Beautiful dark theme UI

## 🔬 How It Works

1. **Server** captures system audio using WASAPI loopback via `soundcard` library
2. Audio is converted to 16-bit PCM and sent over **WebSocket**
3. **Browser client** receives data and plays it using **Web Audio API**
4. **Visualizer** uses AudioContext's AnalyserNode for real-time frequency display

## 📝 Troubleshooting

### No audio captured?
- Make sure audio is playing on your PC
- Check that your default audio output device is working
- Try restarting the server

### High latency?
- Reduce `CHUNK_SIZE` for lower latency (may increase CPU usage)
- Ensure you're on the same network (not through VPN)

### Connection refused?
- Check firewall settings
- Verify the server is running
- Make sure you're using the correct IP address

## 📄 License

MIT License - Feel free to use and modify!

---

Made with ❤️ for seamless audio streaming
