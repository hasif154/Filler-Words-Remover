<<<<<<< HEAD
# 🎬 Filler Moments Remover

**Automatically remove pauses, dead air, and silent moments from your videos.**

A free, open-source tool that uses audio-level detection to tighten video pacing — similar to CapCut and Premiere's silence removal features.

---

## ✅ What This MVP Does

| Feature | Status |
|---------|--------|
| Detect silent/quiet sections | ✅ |
| Cut out pauses and dead air | ✅ |
| Tighten video pacing | ✅ |
| Adjustable margin (buffer) | ✅ |
| Preview processed video | ✅ |
| Download cleaned video | ✅ |

## 🚀 What's Coming in v2 (Whisper)

| Feature | Status |
|---------|--------|
| Word-level "uh/um" detection | 🔜 |
| Semantic filler word removal | 🔜 |
| Preview before export | 🔜 |
| Manual review mode | 🔜 |

---

## 🧪 How to Test Properly

Use videos with:
- **Long thinking pauses** — gaps before/after speaking
- **"uh / um" sounds** — the pauses around them get cut
- **Natural conversation** — interviews, podcasts, vlogs

**💡 If it feels too jumpy →** increase the margin in settings.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- No system FFmpeg required (uses `imageio-ffmpeg`)

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd fillerwordsremover

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## ⚙️ How It Works

Uses **Auto-Editor v29** with audio-level detection:

```bash
auto-editor input.mp4 --margin 0.25s --no-open
```

**Flags used:**
- `--margin` — Buffer time around cuts (default 0.25s)
- `--no-open` — Don't auto-open output file
- Default `--edit audio` — Detects audio levels
- Default `--when-silent cut` — Removes silent sections

No deprecated or unsupported flags. Works on Windows without system FFmpeg.

---

## 🎯 Best Use Cases

- 📹 Talking-head videos / YouTube content
- 🎙️ Podcasts / Interview recordings
- 💼 Presentations / Professional recordings
- 🎓 Educational content / Lectures

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | Web UI |
| Auto-Editor v29 | Video processing |
| imageio-ffmpeg | FFmpeg binaries (no install needed) |

---

## 📁 Project Structure

```
fillerwordsremover/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── venv/               # Virtual environment
```

---

## 🚢 Deployment Options

### 1️⃣ Streamlit Cloud (Free)
```bash
# Push to GitHub, then deploy via streamlit.io/cloud
```

### 2️⃣ Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### 3️⃣ Desktop App (PyInstaller)
```bash
pip install pyinstaller
pyinstaller --onefile app.py
```

---

## 📝 License

MIT License — use freely for personal or commercial projects.

---

**Built with ❤️**

*Same brain as CapCut. Same logic as Premiere. 100% free. Actually useful.*
=======
# Filler-Words-Remover
Creating this as an MVP 
