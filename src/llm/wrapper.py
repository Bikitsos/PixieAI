"""
LLM Wrapper Module

Provides a wrapper class for the MLX-LM inference engine.
"""

from typing import Optional, Callable
import mlx_lm

from src.config import MODEL_ID, MAX_TOKENS, TEMPERATURE, TOP_P


SEARCH_PROMPT_TEMPLATE = (
    "You are PixieAI, a helpful AI assistant. Answer the user's question based on "
    "the provided search context. Be concise and informative. If the context doesn't "
    "contain relevant information, say so and provide your best answer.\n\n"
    "Context from web search:\n{context}\n\n"
    "User Question: {question}\n\n"
    "Answer:"
)


DIRECT_PROMPT_TEMPLATE = (
    "You are PixieAI, a helpful AI assistant. Be concise, informative, and friendly.\n\n"
    "User: {question}\n\n"
    "Assistant:"
)


class LLMWrapper:
    """
    Wrapper class for MLX-LM model inference.
    
    Handles model loading, prompt formatting, and text generation.
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
    
    def _build_prompt(self, question: str, context: Optional[str] = None) -> str:
        """
        Build the prompt for the model.
        
        Args:
            question: User's question.
            context: Optional search context to include.
        
        Returns:
            Formatted prompt string.
        """
        if context:
            return SEARCH_PROMPT_TEMPLATE.format(context=context, question=question)
        return DIRECT_PROMPT_TEMPLATE.format(question=question)
    
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
        
        response = mlx_lm.generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            temp=temperature,
            top_p=top_p,
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
        
        full_response = []
        
        for token in mlx_lm.stream_generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            temp=temperature,
            top_p=top_p,
        ):
            full_response.append(token)
            if callback:
                callback(token)
        
        return "".join(full_response)
