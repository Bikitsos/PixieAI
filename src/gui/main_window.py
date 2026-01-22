"""
Main Window Module

Native macOS-styled chatbot interface for PixieAI.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QCheckBox,
    QLabel, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut

from src.llm import LLMWrapper
from src.gui.worker import WorkerThread


class MessageBubble(QFrame):
    """A single chat message bubble."""
    
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.label = None
        self._setup_ui(text)
    
    def _setup_ui(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(8)
        
        if self.is_user:
            # User message: right-aligned, blue bubble
            layout.addStretch()
            
            bubble = QFrame()
            bubble.setObjectName("userBubble")
            bubble_layout = QVBoxLayout(bubble)
            bubble_layout.setContentsMargins(14, 10, 14, 10)
            
            self.label = QLabel(text)
            self.label.setWordWrap(True)
            self.label.setTextFormat(Qt.TextFormat.PlainText)
            self.label.setStyleSheet("color: white; font-size: 14px;")
            bubble_layout.addWidget(self.label)
            
            bubble.setStyleSheet("""
                QFrame#userBubble {
                    background-color: #007AFF;
                    border-radius: 18px;
                    border-bottom-right-radius: 4px;
                }
            """)
            bubble.setMaximumWidth(400)
            layout.addWidget(bubble)
        else:
            # Bot message: left-aligned with avatar, gray bubble
            avatar = QLabel("P")
            avatar.setFixedSize(28, 28)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet("""
                background-color: #8E44AD;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 14px;
            """)
            layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignTop)
            
            bubble = QFrame()
            bubble.setObjectName("botBubble")
            bubble_layout = QVBoxLayout(bubble)
            bubble_layout.setContentsMargins(14, 10, 14, 10)
            
            self.label = QLabel(text)
            self.label.setWordWrap(True)
            self.label.setTextFormat(Qt.TextFormat.PlainText)
            self.label.setStyleSheet("color: #1C1C1E; font-size: 14px;")
            bubble_layout.addWidget(self.label)
            
            bubble.setStyleSheet("""
                QFrame#botBubble {
                    background-color: #F0F0F5;
                    border-radius: 18px;
                    border-bottom-left-radius: 4px;
                }
            """)
            bubble.setMaximumWidth(400)
            layout.addWidget(bubble)
            layout.addStretch()
    
    def append_text(self, text: str):
        """Append text to the message (for streaming)."""
        if self.label:
            current = self.label.text()
            self.label.setText(current + text)
    
    def set_text(self, text: str):
        """Set the message text."""
        if self.label:
            self.label.setText(text)


class MainWindow(QMainWindow):
    """
    Main chatbot window with native macOS styling.
    """
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Pixie")
        self.setMinimumSize(500, 600)
        self.resize(600, 750)
        
        # Initialize LLM (lazy loading)
        self.llm = LLMWrapper()
        self.worker = None
        self.current_bubble = None
        self.is_streaming = False
        
        self._setup_ui()
        self._setup_shortcuts()
        self._apply_style()
    
    def _setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(70)
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        # Avatar and title
        avatar_label = QLabel("P")
        avatar_label.setFixedSize(40, 40)
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("""
            background-color: #8E44AD;
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 20px;
        """)
        header_layout.addWidget(avatar_label)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title_label = QLabel("Pixie")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        
        self.status_label = QLabel("Online • Ready to chat")
        self.status_label.setObjectName("statusLabel")
        title_layout.addWidget(self.status_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Search toggle in header
        self.search_checkbox = QCheckBox("Web Search")
        self.search_checkbox.setObjectName("searchToggle")
        header_layout.addWidget(self.search_checkbox)
        
        layout.addWidget(header)
        
        # Chat area - scroll area with message bubbles
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("chatScrollArea")
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(8, 16, 8, 16)
        self.chat_layout.setSpacing(8)
        self.chat_layout.addStretch()  # Push messages to top
        
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area, 1)
        
        # Input area
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(16, 16, 16, 16)
        input_layout.setSpacing(12)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message Pixie...")
        self.input_field.setObjectName("inputField")
        self.input_field.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.input_field, 1)
        
        self.send_button = QPushButton("➤")
        self.send_button.setObjectName("sendButton")
        self.send_button.setFixedSize(44, 44)
        self.send_button.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(input_frame)
        
        # Welcome message
        self._add_bot_message("Hi there! I'm Pixie, your friendly AI assistant.\n\nI'm here to help - ask me anything! Enable Web Search for the latest info.\n\nWhat can I help you with today?")
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._on_send)
    
    def _apply_style(self):
        """Apply chatbot styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            
            #header {
                background-color: #F8F9FA;
                border-bottom: 1px solid #E5E5EA;
            }
            
            #titleLabel {
                font-size: 18px;
                font-weight: 600;
                color: #1C1C1E;
            }
            
            #statusLabel {
                font-size: 12px;
                color: #34C759;
            }
            
            #searchToggle {
                font-size: 13px;
                color: #3C3C43;
                padding: 8px 12px;
                background-color: #E5E5EA;
                border-radius: 16px;
            }
            
            #searchToggle:checked {
                background-color: #34C759;
                color: white;
            }
            
            #chatScrollArea {
                background-color: #FFFFFF;
                border: none;
            }
            
            #inputFrame {
                background-color: #F8F9FA;
                border-top: 1px solid #E5E5EA;
            }
            
            #inputField {
                background-color: #FFFFFF;
                border: 2px solid #E5E5EA;
                border-radius: 22px;
                padding: 12px 18px;
                font-size: 15px;
                color: #1C1C1E;
            }
            
            #inputField:focus {
                border-color: #007AFF;
            }
            
            #sendButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
                font-weight: bold;
            }
            
            #sendButton:hover {
                background-color: #0056CC;
            }
            
            #sendButton:pressed {
                background-color: #004499;
            }
            
            #sendButton:disabled {
                background-color: #C7C7CC;
            }
        """)
        
        font = QFont(".AppleSystemUIFont", 14)
        self.setFont(font)
    
    def _scroll_to_bottom(self):
        """Scroll chat to the bottom."""
        QTimer.singleShot(10, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
    
    def _add_user_message(self, text: str):
        """Add a user message bubble."""
        bubble = MessageBubble(text, is_user=True)
        # Insert before the stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self._scroll_to_bottom()
    
    def _add_bot_message(self, text: str):
        """Add a bot message bubble."""
        bubble = MessageBubble(text, is_user=False)
        # Insert before the stretch
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self._scroll_to_bottom()
    
    def _start_bot_message(self):
        """Start a streaming bot message."""
        self.is_streaming = True
        self.current_bubble = MessageBubble("", is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.current_bubble)
        self._scroll_to_bottom()
    
    def _append_token(self, token: str):
        """Append a token to the current streaming message."""
        if self.current_bubble:
            self.current_bubble.append_text(token)
            self._scroll_to_bottom()
    
    def _end_bot_message(self):
        """End the streaming bot message."""
        self.is_streaming = False
        self.current_bubble = None
    
    def _on_send(self):
        """Handle send button click."""
        question = self.input_field.text().strip()
        if not question or self.is_streaming:
            return
        
        # Disable input
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.input_field.clear()
        
        # Show user message
        self._add_user_message(question)
        
        # Update status
        if self.search_checkbox.isChecked():
            self.status_label.setText("Searching...")
            self.status_label.setStyleSheet("color: #FF9500;")
        else:
            self.status_label.setText("Thinking...")
            self.status_label.setStyleSheet("color: #FF9500;")
        
        # Start worker
        self.worker = WorkerThread(self.llm)
        self.worker.set_task(question, self.search_checkbox.isChecked())
        
        self.worker.status_update.connect(self._on_status_update)
        self.worker.token_generated.connect(self._on_token_generated)
        self.worker.generation_complete.connect(self._on_generation_complete)
        self.worker.error_occurred.connect(self._on_error)
        
        self._start_bot_message()
        self.worker.start()
    
    def _on_status_update(self, status: str):
        """Handle status updates."""
        self.status_label.setText(status)
    
    def _on_token_generated(self, token: str):
        """Handle streaming token."""
        self._append_token(token)
    
    def _on_generation_complete(self, response: str):
        """Handle generation completion."""
        self._end_bot_message()
        self.status_label.setText("Online • Ready to chat")
        self.status_label.setStyleSheet("color: #34C759;")
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
    
    def _on_error(self, error: str):
        """Handle errors."""
        self._end_bot_message()
        self._add_bot_message(f"Oops! Something went wrong:\n\n{error}\n\nPlease try again.")
        self.status_label.setText("Error occurred")
        self.status_label.setStyleSheet("color: #FF3B30;")
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
