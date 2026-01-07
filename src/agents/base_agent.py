"""
Base Agent class that all specialized agents inherit from.
Handles common functionality: LLM calls, logging, error handling, rate limiting.
"""

import os
import time
import google.generativeai as genai
from abc import ABC, abstractmethod
from src.utils.logger import log_experiment, ActionType
from src.config import DEFAULT_MODEL, RATE_LIMITS


class BaseAgent(ABC):
    """Abstract base class for all agents in the Refactoring Swarm."""
    
    _last_request_time = 0  # Class variable shared across all agents
    
    def __init__(self, agent_name: str, model_name: str = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name identifier for this agent
            model_name: Gemini model to use (default from config)
        """
        self.agent_name = agent_name
        self.model_name = model_name or DEFAULT_MODEL
        
        # Configure Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # Set rate limit based on model
        self.rate_limit_interval = self._get_rate_limit_interval(self.model_name)
    
    def _get_rate_limit_interval(self, model_name: str) -> float:
        """Get the rate limit interval for the specified model."""
        for model_key, limits in RATE_LIMITS.items():
            if model_key in model_name:
                return limits["interval"]
        return 6.5  # Default conservative interval
    
    def call_llm(self, prompt: str, action_type: ActionType, extra_details: dict = None) -> str:
        """
        Call the LLM and log the interaction with rate limiting.
        
        Args:
            prompt: The prompt to send to the LLM
            action_type: Type of action being performed
            extra_details: Additional details to log
        
        Returns:
            LLM response text
        """
        # Rate limiting: wait if needed
        self._wait_for_rate_limit()
        
        try:
            # Call Gemini with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    response_text = response.text
                    break
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower():
                        # Rate limit error - wait longer
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * self.rate_limit_interval * 2
                            print(f"⚠️  Rate limit hit, waiting {wait_time:.0f}s...")
                            time.sleep(wait_time)
                            continue
                    raise
            
            # Prepare log details
            details = {
                "input_prompt": prompt,
                "output_response": response_text,
            }
            if extra_details:
                details.update(extra_details)
            
            # Log the interaction
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=action_type,
                details=details,
                status="SUCCESS"
            )
            
            return response_text
            
        except Exception as e:
            # Log failure
            error_msg = f"ERROR: {str(e)}"
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=action_type,
                details={
                    "input_prompt": prompt,
                    "output_response": error_msg,
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            raise
    
    def _wait_for_rate_limit(self):
        """Wait to respect rate limits."""
        current_time = time.time()
        time_since_last_request = current_time - BaseAgent._last_request_time
        
        if time_since_last_request < self.rate_limit_interval:
            wait_time = self.rate_limit_interval - time_since_last_request
            time.sleep(wait_time)
        
        BaseAgent._last_request_time = time.time()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent. Must be implemented by subclasses."""
        pass
