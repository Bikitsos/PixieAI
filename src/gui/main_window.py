"""
Main Window Module

Native macOS-styled chat interface for PixieAI.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QCheckBox,
    QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QKeySequence, QShortcut, QTextCursor

from src.llm import LLMWrapper
from src.gui.worker import WorkerThread


class ChatBubble(QFrame):
    """A chat bubble widget for messages."""
    
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_user:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: #007AFF;
                    border-radius: 16px;
                    margin-left: 60px;
                    margin-right: 8px;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                ChatBubble {
                    background-color: #E9E9EB;
                    border-radius: 16px;
                    margin-left: 8px;
                    margin-right: 60px;
                }
                QLabel {
                    color: #1C1C1E;
                    font-size: 14px;
                }
            """)
        
        layout.addWidget(label)


class MainWindow(QMainWindow):
    """
    Main application window with native macOS styling.
    """
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PixieAI")
        self.setMinimumSize(600, 700)
        self.resize(700, 800)
        
        # Initialize LLM (lazy loading)
        self.llm = LLMWrapper()
        self.worker = None
        self.current_response = ""
        
        self._setup_ui()
        self._setup_shortcuts()
        self._apply_macos_style()
    
    def _setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background-color: #F5F5F7;
                border-bottom: 1px solid #D1D1D6;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title_label = QLabel("✨ PixieAI")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #1C1C1E;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #8E8E93;
        """)
        header_layout.addWidget(self.status_label)
        
        layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: none;
                font-size: 14px;
                padding: 16px;
                line-height: 1.5;
            }
        """)
        self.chat_area.setFont(QFont("SF Pro", 14))
        layout.addWidget(self.chat_area, 1)
        
        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F7;
                border-top: 1px solid #D1D1D6;
            }
        """)
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(16, 12, 16, 12)
        input_layout.setSpacing(12)
        
        # Search toggle row
        toggle_layout = QHBoxLayout()
        self.search_checkbox = QCheckBox("🔍 Enable Internet Search")
        self.search_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #3C3C43;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        toggle_layout.addWidget(self.search_checkbox)
        toggle_layout.addStretch()
        input_layout.addLayout(toggle_layout)
        
        # Text input row
        text_input_layout = QHBoxLayout()
        text_input_layout.setSpacing(12)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me anything...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #D1D1D6;
                border-radius: 20px;
                padding: 12px 16px;
                font-size: 14px;
                color: #1C1C1E;
            }
            QLineEdit:focus {
                border-color: #007AFF;
            }
        """)
        self.input_field.returnPressed.connect(self._on_send)
        text_input_layout.addWidget(self.input_field, 1)
        
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
            QPushButton:disabled {
                background-color: #B4B4B4;
            }
        """)
        self.send_button.clicked.connect(self._on_send)
        text_input_layout.addWidget(self.send_button)
        
        input_layout.addLayout(text_input_layout)
        layout.addWidget(input_frame)
        
        # Welcome message
        self._append_message("assistant", "Hello! I'm PixieAI, your local AI assistant powered by Gemma. How can I help you today?\n\n💡 Tip: Enable \"Internet Search\" to get up-to-date information from the web.")
    
    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Cmd+Enter to send
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._on_send)
    
    def _apply_macos_style(self):
        """Apply native macOS styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
        """)
        
        # Use system font
        font = QFont("SF Pro", 14)
        self.setFont(font)
    
    def _append_message(self, role: str, content: str):
        """Append a message to the chat area."""
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if role == "user":
            formatted = f'<div style="text-align: right; margin: 12px 0;"><span style="background-color: #007AFF; color: white; padding: 10px 16px; border-radius: 18px; display: inline-block; max-width: 80%;">{content}</span></div>'
        else:
            formatted = f'<div style="text-align: left; margin: 12px 0;"><span style="background-color: #E9E9EB; color: #1C1C1E; padding: 10px 16px; border-radius: 18px; display: inline-block; max-width: 80%;">{content}</span></div>'
        
        cursor.insertHtml(formatted)
        cursor.insertText("\n")
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()
    
    def _append_streaming_token(self, token: str):
        """Append a streaming token to the current response."""
        self.current_response += token
        
        # Update the last message in the chat
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(token)
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()
    
    def _start_assistant_message(self):
        """Start a new assistant message for streaming."""
        self.current_response = ""
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml('<div style="text-align: left; margin: 12px 0;"><span style="background-color: #E9E9EB; color: #1C1C1E; padding: 10px 16px; border-radius: 18px; display: inline-block;">')
        self.chat_area.setTextCursor(cursor)
    
    def _end_assistant_message(self):
        """End the current assistant message."""
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml('</span></div>')
        cursor.insertText("\n")
        self.chat_area.setTextCursor(cursor)
    
    def _on_send(self):
        """Handle send button click."""
        question = self.input_field.text().strip()
        if not question:
            return
        
        # Disable input while processing
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.input_field.clear()
        
        # Show user message
        self._append_message("user", question)
        
        # Start worker thread
        self.worker = WorkerThread(self.llm)
        self.worker.set_task(question, self.search_checkbox.isChecked())
        
        self.worker.status_update.connect(self._on_status_update)
        self.worker.token_generated.connect(self._on_token_generated)
        self.worker.generation_complete.connect(self._on_generation_complete)
        self.worker.error_occurred.connect(self._on_error)
        
        self._start_assistant_message()
        self.worker.start()
    
    def _on_status_update(self, status: str):
        """Handle status updates from worker."""
        self.status_label.setText(status)
    
    def _on_token_generated(self, token: str):
        """Handle streaming token from worker."""
        self._append_streaming_token(token)
    
    def _on_generation_complete(self, response: str):
        """Handle generation completion."""
        self._end_assistant_message()
        self.status_label.setText("Ready")
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
    
    def _on_error(self, error: str):
        """Handle errors from worker."""
        self._end_assistant_message()
        self._append_message("assistant", f"❌ Error: {error}")
        self.status_label.setText("Error occurred")
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
