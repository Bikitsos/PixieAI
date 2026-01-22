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

## Phase 3: Backend Logic (The "Brain")

### 3.1 Search Module
- [ ] Create search function that accepts user query
- [ ] Return top 3-5 results (limit to save context tokens)
- [ ] Format results as structured string:
  ```
  Title: [Title]
  Snippet: [Text]
  ```

### 3.2 LLM Wrapper Class
- [ ] Initialize model using `mlx_lm.load()`
- [ ] Create `generate()` function accepting:
  - User prompt
  - Optional context string (from search)

### 3.3 Prompt Engineering
- [ ] Design prompt template with search context injection
- [ ] Instruct model to "answer based on the context provided"

**Example Prompt Template:**
```
Context from web search:
{search_results}

User Question: {user_query}

Please answer the question based on the context provided above.
```

---

## Phase 4: GUI Architecture

### 4.1 Interface Design
- [ ] Main window with scrollable chat history
- [ ] Input field for user prompts
- [ ] "Enable Internet Search" toggle/checkbox
- [ ] Send button
- [ ] Status indicator (loading/generating)

### 4.2 Threading Implementation ⚠️ **CRITICAL**

> **Warning:** LLMs are blocking operations. Running on main thread causes UI freeze (Spinning Beach Ball).

- [ ] Create `QThread` Worker class
- [ ] Worker handles:
  - Web search (if enabled)
  - MLX generation
- [ ] Implement signals to update UI from worker thread
- [ ] Never block the main UI thread

**Architecture:**
```
┌─────────────────┐     Signal      ┌─────────────────┐
│   Main Thread   │ ◄────────────── │  Worker Thread  │
│   (GUI/Qt)      │                 │  (Search + LLM) │
└─────────────────┘                 └─────────────────┘
```

---

## Phase 5: Integration & Execution

### 5.1 Connect the Pipeline
- [ ] On "Send" click → disable input button
- [ ] Check search toggle:
  - **Yes:** Run search → Pass results + prompt to LLM
  - **No:** Pass prompt directly to LLM

### 5.2 Streaming Output
- [ ] Set up MLX generation callback
- [ ] Display tokens incrementally (typewriter effect)
- [ ] Avoid bulk text dump at end

### 5.3 Run Application
```bash
uv run app.py
```

---

## Phase 6: Optimization & Quality Checks

### 6.1 Memory Monitoring
- [ ] Open macOS Activity Monitor during generation
- [ ] Verify Python process stays within **6-8 GB** range
- [ ] Check for memory leaks during extended sessions

### 6.2 Model Caching
- [ ] Handle initial model download (~5-6 GB)
- [ ] Show loading state in GUI during download
- [ ] Prevent user thinking app has crashed

### 6.3 Error Handling
- [ ] Network failures (search)
- [ ] Model loading failures
- [ ] Out of memory scenarios

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
| Phase 3: Backend Logic | ⬜ Not Started |
| Phase 4: GUI Architecture | ⬜ Not Started |
| Phase 5: Integration | ⬜ Not Started |
| Phase 6: Optimization | ⬜ Not Started |

---

## 📚 Resources

- [MLX LM Documentation](https://github.com/ml-explore/mlx-examples/tree/main/llms)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search)
- [uv Package Manager](https://github.com/astral-sh/uv)

---

*Last Updated: January 2026*
