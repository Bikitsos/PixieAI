# PixieAI Development Roadmap

> A local AI assistant powered by MLX on Apple Silicon with optional internet search capabilities.

---

## 📋 Overview

| Requirement | Target |
|-------------|--------|
| **RAM Limit** | < 16GB |
| **Model** | Gemma 2 9B (4-bit quantized) |
| **Platform** | macOS (Apple Silicon) |
| **GUI Framework** | PySide6 / PyQt6 |

---

## Phase 1: Environment & Dependency Management ✅

### 1.1 Install uv Package Manager
- [x] Install `uv` (significantly faster than pip, handles virtual environments automatically)
- [x] Verify installation: `uv --version`

### 1.2 Initialize Project
- [x] Create project directory
- [x] Initialize with `uv init`

### 1.3 Add Dependencies
| Package | Purpose |
|---------|---------|
| `mlx-lm` | Apple Silicon optimized inference engine |
| `pyside6` | Native macOS GUI (Qt-based, better for complex threading) |
| `duckduckgo-search` | Internet search without API keys |

```bash
uv add mlx-lm pyside6 duckduckgo-search
```

---

## Phase 2: Model Selection & Memory Strategy ✅

### 2.1 Target Model
- [x] Select **`gemma-2-9b-it-4bit`** (4-bit quantized version)

### 2.2 Memory Budget

| Component | RAM Usage |
|-----------|-----------|
| Gemma 9B (4-bit) | ~6-7 GB |
| macOS + GUI + Browser | ~9 GB |
| **Total** | **< 16 GB** ✅ |

### 2.3 Verify Hardware Acceleration
- [x] Confirm MLX defaults to GPU (Metal) backend
- [x] CPU remains free for GUI and network tasks

---

## Phase 3: Backend Logic (The "Brain") ✅

### 3.1 Search Module
- [x] Create search function that accepts user query
- [x] Return top 3-5 results (limit to save context tokens)
- [x] Format results as structured string:
  ```
  Title: [Title]
  Snippet: [Text]
  ```

### 3.2 LLM Wrapper Class
- [x] Initialize model using `mlx_lm.load()`
- [x] Create `generate()` function accepting:
  - User prompt
  - Optional context string (from search)

### 3.3 Prompt Engineering
- [x] Design prompt template with search context injection
- [x] Instruct model to "answer based on the context provided"

**Example Prompt Template:**
```
Context from web search:
{search_results}

User Question: {user_query}

Please answer the question based on the context provided above.
```

---

## Phase 4: GUI Architecture ✅

### 4.1 Interface Design
- [x] Main window with scrollable chat history
- [x] Input field for user prompts
- [x] "Enable Internet Search" toggle/checkbox
- [x] Send button
- [x] Status indicator (loading/generating)

### 4.2 Threading Implementation ⚠️ **CRITICAL**

> **Warning:** LLMs are blocking operations. Running on main thread causes UI freeze (Spinning Beach Ball).

- [x] Create `QThread` Worker class
- [x] Worker handles:
  - Web search (if enabled)
  - MLX generation
- [x] Implement signals to update UI from worker thread
- [x] Never block the main UI thread

**Architecture:**
```
┌─────────────────┐     Signal      ┌─────────────────┐
│   Main Thread   │ ◄────────────── │  Worker Thread  │
│   (GUI/Qt)      │                 │  (Search + LLM) │
└─────────────────┘                 └─────────────────┘
```

---

## Phase 5: Integration & Execution ✅

### 5.1 Connect the Pipeline
- [x] On "Send" click → disable input button
- [x] Check search toggle:
  - **Yes:** Run search → Pass results + prompt to LLM
  - **No:** Pass prompt directly to LLM

### 5.2 Streaming Output
- [x] Set up MLX generation callback
- [x] Display tokens incrementally (typewriter effect)
- [x] Avoid bulk text dump at end

### 5.3 Run Application
```bash
uv run main.py
```

---

## Phase 6: Optimization & Quality Checks ✅

### 6.1 Memory Monitoring
- [x] Open macOS Activity Monitor during generation
- [x] Verify Python process stays within **6-8 GB** range
- [x] Check for memory leaks during extended sessions

### 6.2 Model Caching
- [x] Handle initial model download (~5-6 GB)
- [x] Show loading state in GUI during download
- [x] Prevent user thinking app has crashed

### 6.3 Error Handling
- [x] Network failures (search)
- [x] Model loading failures
- [x] Out of memory scenarios

---

## 📁 Suggested Project Structure

```
PixieAI/
├── pyproject.toml
├── README.md
├── ROADMAP.md
├── src/
│   ├── __init__.py
│   ├── app.py              # Entry point
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py  # Qt main window
│   │   └── worker.py       # QThread worker
│   ├── llm/
│   │   ├── __init__.py
│   │   └── wrapper.py      # MLX LLM wrapper
│   └── search/
│       ├── __init__.py
│       └── web_search.py   # DuckDuckGo integration
└── tests/
    └── ...
```

---

## ✅ Completion Checklist

| Phase | Status |
|-------|--------|
| Phase 1: Environment Setup | ✅ Complete |
| Phase 2: Model Strategy | ✅ Complete |
| Phase 3: Backend Logic | ✅ Complete |
| Phase 4: GUI Architecture | ✅ Complete |
| Phase 5: Integration | ✅ Complete |
| Phase 6: Optimization | ✅ Complete |

---

## 📚 Resources

- [MLX LM Documentation](https://github.com/ml-explore/mlx-examples/tree/main/llms)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search)
- [uv Package Manager](https://github.com/astral-sh/uv)

---

*Last Updated: January 2026*
