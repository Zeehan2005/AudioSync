# AudioSync

<p align="center">
  <strong>بسم الله الرحمان الرحيم</strong><br>
  <strong>اللهم علمنا ما ينفعنا، وانفعنا بما علمتنا، وزدنا علما</strong>
</p>

---

<p align="center">
  <img src="assets/phone-icon.png" alt="Phone App" width="100"/>
  &nbsp;&nbsp;&nbsp;➡️&nbsp;&nbsp;&nbsp;
  <img src="assets/pc-icon.png" alt="PC Receiver" width="100"/>
</p>

<p align="center">
  <strong>Stream audio from your Android phone to your Windows PC in real-time.</strong>
</p>

AudioSync is an open-source project that lets you use your phone as a wireless audio source for your PC. Perfect for:
- 🎧 Listening to phone audio through PC speakers/headphones
- 🎮 Gaming with phone audio output
- 📺 Watching content with low-latency audio sync

---

## Features

- **Multiple Connection Methods:**
  - 📶 **LAN (Wi-Fi)** - Stream over your local network
  - 🔌 **USB Tether** - Ultra-low latency via USB debugging
  - 🔵 **Bluetooth A2DP** - Wireless with no app needed on phone (experimental)

- **PC Receiver:**
  - Modern Electron-based UI
  - System tray support (minimize to tray)
  - Customizable audio buffer for latency tuning
  - Global keyboard shortcuts for volume control
  - Auto-updates with delta downloads
  - 🔵 **Bluetooth AVRCP + Windows SMTC** - phone media buttons & PC media keys control playback, with a "Now playing" card (Bluetooth mode)

- **Android Sender:**
  - Stream system audio (Android 10+)
  - Simple, intuitive interface
  - Background streaming support

---

## Requirements

| Platform | Minimum Version |
|----------|-----------------|
| **Android** | Android 10 (API 29) or higher |
| **Windows** | Windows 10 or higher |

---

## Download

### PC Receiver (Windows)
Download the latest installer from [Releases](https://github.com/Kurei1/AudioSync/releases).

### Android App
Download the APK from [Releases](https://github.com/Kurei1/AudioSync/releases) or build from source.

---

## Project Structure

```
AudioSync/
├── PC/                     # Windows desktop receiver
│   ├── react/              # Electron + React UI
│   └── pc_receiver/        # Python audio backend
│
├── PHONE/                  # Android sender app
│   ├── app/                # Android source code
│   └── ...                 # Gradle build files
│
└── README.md               # This file
```

---

## Building from Source

### PC Receiver
```bash
cd PC/react
npm install
npm run electron:build    # Creates installer
```

### Android App
```bash
cd PHONE
./gradlew assembleDebug   # Creates APK
```

---

---

## Configuration

**Important:** This project uses Firebase for feedback and bug reporting. You must provide your own Firebase configuration.

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Enable **Firestore Database** and **Authentication** (Anonymous auth)
3. Copy `PC/react/firebase-config.example.js` to `PC/react/firebase-config.js`
4. Fill in your project details:
   ```javascript
   const firebaseConfig = {
       apiKey: "YOUR_API_KEY",
       // ... other values
   };
   const appId = "your-app-id"; 
   ```

---

## Quick Start

1. Install the PC receiver and Android app
2. Connect both devices to the same Wi-Fi network
3. Start the PC receiver and note the IP address
4. Enter the IP in the Android app and tap "Start"
5. Audio from your phone now plays on your PC!

---

## Connection Methods

### 📶 Wi-Fi (LAN)
Stream audio over your local network. Both devices must be on the same Wi-Fi.
- **Latency:** ~20-60ms
- **Requirements:** Both devices on same network

### 🔌 USB Tether
Ultra-low latency via USB debugging (ADB).
- **Latency:** ~0-20ms
- **Requirements:** USB cable, USB debugging enabled on phone

### 🔵 Bluetooth A2DP (Experimental)
Makes your PC act as a Bluetooth speaker. Your phone sends audio directly via Bluetooth.
- **Latency:** ~0-20ms
- **Requirements:** Bluetooth on both devices, `winsdk` and `pyaudio` Python packages
- **No Android app needed** - just pair and play!
- **AVRCP + System Media Transport Controls (SMTC):** When the PC is the A2DP sink,
  AudioSync also registers with Windows **SMTC** so that:
  - A **"Now playing"** card appears in the Windows Action Center / lock screen showing
    AudioSync as the player.
  - **AVRCP** commands from your phone (play / pause / next / previous / stop, sent from
    the handset's media buttons) and your PC's own **media keys** are delivered to
    AudioSync through SMTC and reflected back to the phone, keeping the play/pause state
    in sync on both sides.
  - Implementation: `PC/pc_receiver/smtc_control.py` (WinRT
    `Windows.Media.SystemMediaTransportControls`) wired into
    `PC/pc_receiver/bluetooth_receiver.py`.
  - Note: volume is still handled by the phone over AVRCP absolute-volume and applied by
    Windows to the Bluetooth endpoint directly. Audio muting on *pause* is currently
    limited by the experimental A2DP-sink audio path; the SMTC playback state is always
    kept in sync.


---

## From the Developer

> Hello there, I just wanted to leave this message so you know exactly what this is. This is a project that I have worked on in 4 days. It's fully using an AI agent. Also, I want to note that I have no idea how to code (I don't even know Python), so there might be some mistakes in the project that I wouldn't notice. For the people who want to build projects out there but don't know the language, take me as an example—all I know is a little bit of English (I even asked the AI agent to correct my message: "Do not change it, just correct my grammar and spelling mistakes"). You don't need to know much to do something; just start and seek for alternatives and workarounds. Thank you for listening. — Kurei

---

## Support the Developer

AudioSync is free and open source. If you find it useful, consider supporting:

- ☕ **PayPal:** animecore2020@gmail.com
- 💰 **Binance Pay:** ID 763038084
- 💰 **ByBit:** ID 416909609
- 📱 **Instagram:** [@kurei.111](https://instagram.com/kurei.111)
- 📧 **Email:** audio.sync.2025@gmail.com

---

## License

MIT License - Feel free to use, modify, and distribute.

---

Made with ❤️ by [Kurei](https://github.com/Kurei1)
