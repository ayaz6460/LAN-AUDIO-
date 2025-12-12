<div align="center">

# 🎵 LAN Audio Streamer

### Stream Windows System Audio to Any Device on Your Network

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-orange?style=for-the-badge&logo=socket.io&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

<p align="center">
  <strong>No apps. No drivers. Just open a browser and listen.</strong>
</p>

---

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [Configuration](#-configuration) • [Troubleshooting](#-troubleshooting)

</div>

---

## 🌟 What is LAN Audio Streamer?

LAN Audio Streamer captures your Windows PC's system audio in real-time and streams it to any device on your local network through a web browser. Whether you want to:

- 🎧 Listen to your PC audio on wireless earbuds connected to your phone
- 🔊 Use your phone as an extra speaker
- 📱 Watch videos on PC while listening on another device
- 🎮 Stream game audio to multiple devices

**It just works** - with minimal latency and maximum quality.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Core Features
- **Real-time Streaming** - Low latency audio over WebSocket
- **WASAPI Loopback** - Direct capture from sound card
- **Multi-Client** - Stream to unlimited devices
- **Zero Installation** - Browser-based client

</td>
<td width="50%">

### 🎨 User Experience  
- **Beautiful UI** - Modern dark theme with animations
- **Live Visualizer** - Real-time audio frequency bars
- **Responsive Design** - Works on any screen size
- **Auto-Reconnect** - Seamless connection recovery

</td>
</tr>
<tr>
<td width="50%">

### ⚡ Performance
- **48kHz Audio** - High-quality streaming
- **~80ms Latency** - Near real-time playback
- **Smart Buffering** - Smooth, gap-free audio
- **Efficient Protocol** - Binary WebSocket data

</td>
<td width="50%">

### 🛠️ Technical
- **PyAudioWPatch** - Reliable Windows audio capture
- **aiohttp** - Async Python web server
- **Web Audio API** - Browser audio processing
- **WebSocket** - Full-duplex communication

</td>
</tr>
</table>

---

## 📋 Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10 / 11 |
| **Python** | 3.8 or higher |
| **Audio** | Any output device (speakers/headphones) |
| **Network** | Local network (WiFi/Ethernet) |
| **Browser** | Chrome, Firefox, Edge, Safari (modern) |

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/lan-audio-stream.git
cd lan-audio-stream
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Server

```bash
python server.py
```

You'll see:
```
============================================================
  🎵 LAN Audio Streamer
============================================================

  Server running at:
    • Local:   http://localhost:8765
    • Network: http://192.168.x.x:8765

  Open the URL on any device on your network to listen!
============================================================
```

### 4️⃣ Connect & Listen

Open the **Network URL** on any device (phone, tablet, another PC) and press **Play**! 🎉

---

## 📱 Usage

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                    🎵 LAN Audio Stream                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│         ████  ██  ████  ██  ████  ██  ████  ██              │
│         ████  ██  ████  ██  ████  ██  ████  ██              │
│         ████████  ████████  ████████  ████████              │
│                    [ Audio Visualizer ]                      │
│                                                             │
│                     ●  Connected                            │
│                                                             │
│                      [ ▶ PLAY ]                             │
│                                                             │
│              🔊 ━━━━━━━━━━━━━●━━━━━━ 75%                    │
│                                                             │
│        Latency: 45ms  •  Buffer: 6  •  48kHz               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

</div>

1. **Start the server** on your Windows PC
2. **Open the URL** on any device on the same network
3. **Click Play** to begin streaming
4. **Adjust volume** with the slider
5. **Monitor stats** - latency, buffer, sample rate

---

## 🔧 Configuration

### Server Settings (`server.py`)

```python
SAMPLE_RATE = 48000   # Audio quality (Hz) - higher = better quality
CHANNELS = 2          # 1 = Mono, 2 = Stereo
CHUNK_SIZE = 1920     # Samples per chunk - lower = less latency
PORT = 8765           # Server port number
```

### Client Settings (`static/index.html`)

```javascript
const TARGET_LATENCY_MS = 80;    // Target delay (ms)
const MIN_BUFFER_SIZE = 4;       // Minimum buffers before playback
const TARGET_BUFFER_SIZE = 6;    // Optimal buffer count
```

### Latency vs Stability Trade-off

| Setting | Low Latency | Balanced | High Stability |
|---------|-------------|----------|----------------|
| `CHUNK_SIZE` | 960 | 1920 | 4096 |
| `TARGET_LATENCY_MS` | 50 | 80 | 200 |
| `MIN_BUFFER_SIZE` | 2 | 4 | 6 |

---

## 🛡️ Firewall Configuration

If clients can't connect, allow the port through Windows Firewall:

### Option 1: PowerShell (Run as Admin)

```powershell
netsh advfirewall firewall add rule name="LAN Audio Stream" dir=in action=allow protocol=tcp localport=8765
```

### Option 2: Windows Settings

1. Open **Windows Security** → **Firewall & network protection**
2. Click **Allow an app through firewall**
3. Add **Python** or the specific port **8765**

---

## 🔬 How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                        ARCHITECTURE                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    WASAPI     ┌─────────────┐                  │
│  │   Windows   │   Loopback    │   Python    │                  │
│  │    Audio    │ ────────────► │   Server    │                  │
│  │   Output    │               │  (aiohttp)  │                  │
│  └─────────────┘               └──────┬──────┘                  │
│                                       │                          │
│                              WebSocket (Binary PCM)              │
│                                       │                          │
│                    ┌──────────────────┼──────────────────┐      │
│                    ▼                  ▼                  ▼      │
│             ┌───────────┐      ┌───────────┐      ┌───────────┐ │
│             │  Browser  │      │  Browser  │      │  Browser  │ │
│             │  Client 1 │      │  Client 2 │      │  Client N │ │
│             │ (Phone)   │      │ (Tablet)  │      │   (PC)    │ │
│             └───────────┘      └───────────┘      └───────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Capture** - PyAudioWPatch captures system audio via WASAPI loopback
2. **Encode** - Audio converted to 16-bit PCM (raw, no compression)
3. **Stream** - Binary data sent over WebSocket to all clients
4. **Decode** - Browser converts PCM to Float32 audio samples
5. **Play** - Web Audio API schedules gapless buffer playback
6. **Visualize** - AnalyserNode provides real-time frequency data

---

## 📝 Troubleshooting

<details>
<summary><b>🔇 No audio captured?</b></summary>

- Ensure audio is playing on your PC
- Check your default audio output device is working
- Restart the server after changing audio devices
- Verify PyAudioWPatch is properly installed

</details>

<details>
<summary><b>⏱️ High latency / delay?</b></summary>

- Reduce `CHUNK_SIZE` in `server.py` (try 960)
- Lower `TARGET_LATENCY_MS` in client (try 50)
- Ensure you're on the same local network
- Don't use VPN - it adds latency
- Use 5GHz WiFi instead of 2.4GHz

</details>

<details>
<summary><b>🔌 Connection refused?</b></summary>

- Check Windows Firewall settings
- Verify the server is running (check terminal)
- Make sure you're using the correct IP address
- Try `localhost:8765` from the same PC first

</details>

<details>
<summary><b>🔊 Audio crackling / cutting?</b></summary>

- Increase `CHUNK_SIZE` (try 4096)
- Increase `TARGET_LATENCY_MS` (try 200)
- Increase `MIN_BUFFER_SIZE` (try 6)
- Check network stability

</details>

<details>
<summary><b>📱 Not working on mobile?</b></summary>

- Ensure phone is on same WiFi network
- Use the Network URL, not localhost
- Try refreshing the page
- Check if browser supports Web Audio API

</details>

---

## 🗂️ Project Structure

```
lan-audio-stream/
├── server.py           # Python WebSocket server with audio capture
├── static/
│   └── index.html      # Web client (HTML + CSS + JavaScript)
├── requirements.txt    # Python dependencies
├── start.bat          # Windows quick-start script
├── README.md          # This file
└── .gitignore         # Git ignore rules
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### Made with ❤️ by Ayaz

**Stream your audio, anywhere on your network.**

⭐ Star this repo if you find it useful!

</div>
