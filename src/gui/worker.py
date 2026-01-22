"""
Worker Thread Module

Handles background processing for LLM generation and web search.
"""

from PyQt6.QtCore import QThread, pyqtSignal as Signal

from src.llm import LLMWrapper
from src.search import search_and_format


class WorkerThread(QThread):
    """
    Background worker thread for LLM inference.
    
    Prevents UI freezing during model loading and text generation.
    """
    
    # Signals to communicate with main thread
    token_generated = Signal(str)      # Emitted for each token (streaming)
    generation_complete = Signal(str)  # Emitted when generation finishes
    status_update = Signal(str)        # Emitted for status messages
    error_occurred = Signal(str)       # Emitted on error
    
    def __init__(self, llm: LLMWrapper, parent=None):
        super().__init__(parent)
        self.llm = llm
        self.question = ""
        self.use_search = False
    
    def set_task(self, question: str, use_search: bool = False):
        """Set the task parameters before starting the thread."""
        self.question = question
        self.use_search = use_search
    
    def run(self):
        """Execute the task in the background thread."""
        try:
            context = None
            
            # Perform web search if enabled
            if self.use_search:
                self.status_update.emit("Searching the web...")
                context = search_and_format(self.question)
                if context:
                    self.status_update.emit("Search complete. Generating response...")
                else:
                    self.status_update.emit("No search results. Generating response...")
            else:
                self.status_update.emit("Generating response...")
            
            # Load model if not already loaded
            if not self.llm.is_loaded():
                self.status_update.emit("Loading model (first run may take a minute)...")
                self.llm.load()
            
            # Generate response with streaming
            full_response = self.llm.generate_stream(
                question=self.question,
                context=context,
                callback=lambda token: self.token_generated.emit(token)
            )
            
            self.generation_complete.emit(full_response)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
