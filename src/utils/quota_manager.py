"""
Quota Manager - Tracks and limits API usage to prevent quota exhaustion
"""

import time
from typing import Dict
from datetime import datetime


class QuotaManager:
    """
    Simple quota manager for tracking API calls and preventing rate limit issues.
    Singleton pattern ensures one manager tracks all agents.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.call_count: int = 0
        self.agent_calls: Dict[str, int] = {}
        self.start_time: float = time.time()
        self.last_call_time: float = 0
        self.min_delay: float = 1.0  # Minimum 1 second between calls
    
    def check_and_record(self, agent_name: str) -> bool:
        """
        Check if call is allowed and record it.
        
        Args:
            agent_name: Name of the agent making the call
            
        Returns:
            True if call is allowed
        """
        # Simple rate limiting: enforce minimum delay between calls
        current_time = time.time()
        time_since_last = current_time - self.last_call_time
        
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            print(f"⏱️  Rate limit: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        # Record the call
        self.call_count += 1
        self.agent_calls[agent_name] = self.agent_calls.get(agent_name, 0) + 1
        self.last_call_time = time.time()
        
        return True
    
    def get_stats(self) -> Dict:
        """Get usage statistics."""
        elapsed = time.time() - self.start_time
        return {
            "total_calls": self.call_count,
            "elapsed_seconds": elapsed,
            "calls_per_minute": (self.call_count / elapsed * 60) if elapsed > 0 else 0,
            "agent_breakdown": self.agent_calls
        }
    
    def reset(self):
        """Reset all counters."""
        self.call_count = 0
        self.agent_calls = {}
        self.start_time = time.time()
        self.last_call_time = 0


# Global singleton instance
def get_quota_manager() -> QuotaManager:
    """Get the global quota manager instance."""
    return QuotaManager()
