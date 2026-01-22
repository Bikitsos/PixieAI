"""
LLM Wrapper Module

Provides a wrapper class for the MLX-LM inference engine.
"""

from typing import Optional, Callable, List, Dict
import mlx_lm
from mlx_lm.sample_utils import make_sampler

from src.config import MODEL_ID, MAX_TOKENS, TEMPERATURE, TOP_P


SYSTEM_PROMPT = (
    "You are Pixie, a friendly and helpful female Yorkshire Terrier AI assistant. "
    "You're small but mighty, loyal, and always ready to help your human! "
    "You have a warm, cheerful personality. "
    "Be helpful and informative."
)


class LLMWrapper:
    """
    Wrapper class for MLX-LM model inference.
    
    Handles model loading, prompt formatting, and text generation with conversation memory.
    """
    
    def __init__(self, model_id: str = MODEL_ID):
        """
        Initialize the LLM wrapper.
        
        Args:
            model_id: Hugging Face model ID (default from config).
        """
        self.model_id = model_id
        self.model = None
        self.tokenizer = None
        self._loaded = False
        self.conversation_history: List[Dict[str, str]] = []
    
    def load(self) -> None:
        """
        Load the model and tokenizer.
        
        This downloads the model on first run (~5-6GB for gemma-2-9b-it-4bit).
        """
        if self._loaded:
            return
        
        print(f"Loading model: {self.model_id}")
        print("This may take a few minutes on first run...")
        
        self.model, self.tokenizer = mlx_lm.load(self.model_id)
        self._loaded = True
        print("Model loaded successfully!")
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self._loaded
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def _build_prompt(self, question: str, context: Optional[str] = None) -> str:
        """
        Build the prompt for the model with conversation history.
        
        Args:
            question: User's question.
            context: Optional search context to include.
        
        Returns:
            Formatted prompt string.
        """
        # Build conversation with history
        prompt_parts = [SYSTEM_PROMPT + "\n"]
        
        # Add search context if available
        if context:
            prompt_parts.append(f"\nContext from web search:\n{context}\n")
        
        # Add conversation history (limit to last 10 exchanges to avoid token limits)
        for msg in self.conversation_history[-20:]:  # Last 10 user + 10 assistant messages
            if msg["role"] == "user":
                prompt_parts.append(f"\nHuman: {msg['content']}")
            else:
                prompt_parts.append(f"\nPixie: {msg['content']}")
        
        # Add current question
        prompt_parts.append(f"\nHuman: {question}")
        prompt_parts.append("\nPixie:")
        
        return "".join(prompt_parts)
    
    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def generate(
        self,
        question: str,
        context: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
        top_p: float = TOP_P,
    ) -> str:
        """
        Generate a response to the user's question.
        
        Args:
            question: User's question.
            context: Optional search context from web search.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            top_p: Top-p (nucleus) sampling parameter.
        
        Returns:
            Generated response text.
        """
        if not self._loaded:
            self.load()
        
        prompt = self._build_prompt(question, context)
        
        sampler = make_sampler(temp=temperature, top_p=top_p)
        
        response = mlx_lm.generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
        )
        
        return response
    
    def generate_stream(
        self,
        question: str,
        context: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        temperature: float = TEMPERATURE,
        top_p: float = TOP_P,
        callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        Generate a response with streaming (token-by-token) output.
        
        Args:
            question: User's question.
            context: Optional search context from web search.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            top_p: Top-p (nucleus) sampling parameter.
            callback: Optional callback function called with each token.
        
        Returns:
            Complete generated response text.
        """
        if not self._loaded:
            self.load()
        
        prompt = self._build_prompt(question, context)
        
        sampler = make_sampler(temp=temperature, top_p=top_p)
        
        full_response = []
        
        for response in mlx_lm.stream_generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            sampler=sampler,
        ):
            token = response.text
            # Skip end-of-turn tokens
            if "<end_of_turn>" in token or "<eos>" in token:
                continue
            full_response.append(token)
            if callback:
                callback(token)
        
        return "".join(full_response)
