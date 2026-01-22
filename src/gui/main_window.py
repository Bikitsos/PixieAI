"""
Main Window Module

Native macOS-styled chatbot interface for PixieAI.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QCheckBox,
    QLabel, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QKeySequence, QShortcut, QTextCursor

from src.llm import LLMWrapper
from src.gui.worker import WorkerThread


class MainWindow(QMainWindow):
    """
    Main chatbot window with native macOS styling.
    """
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Pixie 🐕")
        self.setMinimumSize(500, 600)
        self.resize(600, 750)
        
        # Initialize LLM (lazy loading)
        self.llm = LLMWrapper()
        self.worker = None
        self.current_response = ""
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
        avatar_label = QLabel("🐕")
        avatar_label.setStyleSheet("font-size: 32px;")
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
        self.search_checkbox = QCheckBox("🌐 Web Search")
        self.search_checkbox.setObjectName("searchToggle")
        header_layout.addWidget(self.search_checkbox)
        
        layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setObjectName("chatArea")
        self.chat_area.setFont(QFont(".AppleSystemUIFont", 14))
        layout.addWidget(self.chat_area, 1)
        
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
        self._add_bot_message("*wags tail excitedly* 🐕✨\n\nWoof! Hi there, human! I'm Pixie, your adorable Yorkshire Terrier AI!\n\nI'm small but mighty - ask me anything and I'll fetch the best answer! Enable 🌐 Web Search for the latest info!\n\n*tilts head curiously* What can I help you with today?")
    
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
            
            #chatArea {
                background-color: #FFFFFF;
                border: none;
                padding: 20px;
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
    
    def _add_user_message(self, text: str):
        """Add a user message bubble."""
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        html = f'''
        <div style="text-align: right; margin: 8px 0; clear: both;">
            <div style="display: inline-block; background-color: #007AFF; color: white; 
                        padding: 12px 16px; border-radius: 18px 18px 4px 18px; 
                        max-width: 75%; text-align: left; font-size: 14px;">
                {text}
            </div>
        </div>
        '''
        cursor.insertHtml(html)
        cursor.insertBlock()
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()
    
    def _add_bot_message(self, text: str):
        """Add a bot message bubble."""
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Convert newlines to <br>
        text_html = text.replace('\n', '<br>')
        
        html = f'''
        <div style="text-align: left; margin: 8px 0; clear: both;">
            <span style="font-size: 20px; vertical-align: top;">🐕</span>
            <div style="display: inline-block; background-color: #F0F0F5; color: #1C1C1E; 
                        padding: 12px 16px; border-radius: 18px 18px 18px 4px; 
                        max-width: 75%; margin-left: 8px; font-size: 14px;">
                {text_html}
            </div>
        </div>
        '''
        cursor.insertHtml(html)
        cursor.insertBlock()
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()
    
    def _start_bot_message(self):
        """Start a streaming bot message."""
        self.current_response = ""
        self.is_streaming = True
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        html = '''
        <div style="text-align: left; margin: 8px 0; clear: both;">
            <span style="font-size: 20px; vertical-align: top;">🐕</span>
            <span style="display: inline-block; background-color: #F0F0F5; color: #1C1C1E; 
                        padding: 12px 16px; border-radius: 18px 18px 18px 4px; 
                        max-width: 75%; margin-left: 8px; font-size: 14px;">
        '''
        cursor.insertHtml(html)
        self.chat_area.setTextCursor(cursor)
    
    def _append_token(self, token: str):
        """Append a token to the current streaming message."""
        self.current_response += token
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(token)
        self.chat_area.setTextCursor(cursor)
        self.chat_area.ensureCursorVisible()
    
    def _end_bot_message(self):
        """End the streaming bot message."""
        self.is_streaming = False
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml('</span></div>')
        cursor.insertBlock()
        self.chat_area.setTextCursor(cursor)
    
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
            self.status_label.setText("🔍 Searching...")
            self.status_label.setStyleSheet("color: #FF9500;")
        else:
            self.status_label.setText("💭 Thinking...")
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
        self._add_bot_message(f"*whimpers* 😢 Oops! Something went wrong:\n\n{error}\n\n*paws at you hopefully* Can we try again?")
        self.status_label.setText("⚠️ Error occurred")
        self.status_label.setStyleSheet("color: #FF3B30;")
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
