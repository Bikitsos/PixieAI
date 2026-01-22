# ✨ PixieAI

A local AI assistant for macOS powered by MLX and Gemma, with optional internet search.

![Python](https://img.shields.io/badge/python-3.14+-blue)
![Platform](https://img.shields.io/badge/platform-macOS%20(Apple%20Silicon)-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🚀 **Fast Local Inference** - Runs Gemma 2 9B on Apple Silicon using MLX
- 🔍 **Internet Search** - Optional DuckDuckGo integration for up-to-date answers
- 🎨 **Native macOS UI** - Beautiful chatbot-style interface with message bubbles
- 💾 **Memory Efficient** - 4-bit quantization fits in <16GB RAM
- 🔒 **Private** - All processing happens locally on your Mac
- ⚡ **Streaming** - Real-time token-by-token responses

## Screenshots

The app features a clean chatbot interface with:
- Separate message bubbles for user and assistant
- Status indicator (Online, Thinking, Searching)
- Web Search toggle for internet-enhanced answers

## Requirements

- macOS with Apple Silicon (M1/M2/M3)
- 16GB RAM recommended
- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/Bikitsos/PixieAI.git
cd PixieAI

# Install dependencies with uv
uv sync
```

## Usage

```bash
# Run the application
uv run main.py
```

On first run, the app will download the Gemma model (~5-6GB). This only happens once.

### Features

- **Chat**: Type your question and press Enter or click Send
- **Web Search**: Toggle to include DuckDuckGo search results in responses
- **Streaming**: Responses appear token-by-token in real-time

## Project Structure

```
PixieAI/
├── main.py              # Entry point
├── assets/
│   └── icon.png         # App icon
├── src/
│   ├── app.py           # Application launcher
│   ├── config.py        # Configuration settings
│   ├── gui/
│   │   ├── main_window.py   # Chatbot UI with message bubbles
│   │   └── worker.py        # Background thread for LLM
│   ├── llm/
│   │   └── wrapper.py       # MLX LLM wrapper
│   └── search/
│       └── __init__.py      # DuckDuckGo search
├── pyproject.toml
└── ROADMAP.md
```

## Configuration

Edit `src/config.py` to customize:

- `MODEL_ID` - Hugging Face model to use
- `MAX_TOKENS` - Maximum response length
- `TEMPERATURE` - Creativity (0.0-1.0)
- `MAX_SEARCH_RESULTS` - Number of web results

## Tech Stack

- **MLX** - Apple's ML framework for Apple Silicon
- **Gemma 2 9B (4-bit)** - Google's efficient language model
- **PyQt6** - Cross-platform GUI framework
- **ddgs** - DuckDuckGo search API

## License

MIT License - see [LICENSE](LICENSE) for details.
