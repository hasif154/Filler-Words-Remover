# 🎬 Filler Words Remover

**Automatically remove "uh", "um", and awkward pauses from your videos using AI.**

---

## ✨ Features

- 🧠 **AI-Powered** - Uses OpenAI's Whisper for accurate speech recognition
- ⚡ **Fast Processing** - Optimized video editing pipeline
- 🎯 **Customizable** - Control which filler words to remove
- 📊 **Real-time Stats** - See how much time you saved
- 🎨 **Beautiful UI** - Polished, professional interface
- 💯 **100% Free** - No watermarks, no limits

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system

### Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd fillerwordsremover
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🧪 How to Test Properly

Use videos with:
- **"uh / um"** - Common filler words
- **Long thinking pauses** - Natural breaks in speech  
- **Natural conversation** - Interviews, podcasts, vlogs

**💡 Pro tip:** If the video feels too jumpy → increase the margin in settings.

---

## 🎯 Best Use Cases

- 📹 **Talking-head videos** - YouTube content, vlogs
- 🎙️ **Podcasts** - Interview recordings
- 💼 **Presentations** - Professional recordings
- 🎓 **Educational content** - Lectures, tutorials

---

## ⚙️ Settings Explained

### Filler Words
Choose which words to remove:
- "uh" - Most common filler
- "um" - Second most common
- "like" - Conversational filler

### Pause Detection
Remove awkward silences longer than the specified duration.

### Cut Margin
Buffer time before/after cuts. Increase if video feels too jumpy.

### AI Model
- **tiny** - Fastest, least accurate
- **base** - Good balance (recommended)
- **small** - More accurate, slower
- **medium** - Most accurate, slowest

---

## 🚀 Next Steps

This is a fully functional MVP. Here's how to take it further:

### 1️⃣ Package as Desktop App
- Use PyInstaller or Electron
- Create installers for Windows/Mac/Linux

### 2️⃣ Deploy to Cloud
- Streamlit Cloud (free tier)
- AWS/GCP/Azure
- Add user authentication

### 3️⃣ Brand & Market
- Choose a catchy name
- Create landing page
- Build social media presence

### 4️⃣ Advanced Features
- Preview before export
- Manual review mode
- Export audio only
- Batch processing
- Human-like cut transitions

---

## 🛠️ Tech Stack

- **Streamlit** - Web interface
- **Whisper AI** - Speech recognition
- **MoviePy** - Video editing
- **FFmpeg** - Media processing

---

## 📝 License

MIT License - feel free to use this for your own projects!

---

## 💬 Support

Found a bug? Have a feature request? Open an issue!

---

**Built with ❤️ by [Your Name]**

*Same brain as CapCut. Same logic as Premiere. 100% free. Actually useful.*
