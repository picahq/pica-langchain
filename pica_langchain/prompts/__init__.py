"""
System prompts for the Pica LangChain integration.
"""

from .default_system import get_default_system_prompt
from .authkit_system import get_authkit_system_prompt
from typing import Optional

def generate_full_system_prompt(system_prompt: str, user_system_prompt: Optional[str] = None) -> str:
    """
    Generate a complete system prompt for use with LLMs.
    
    Args:
        system_prompt: The Pica system prompt.
        user_system_prompt: Optional custom system prompt to prepend.
        
    Returns:
        The complete system prompt including Pica connection information.
    """
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc)
    prompt = f"""{ user_system_prompt or "" }
=== PICA: INTEGRATION ASSISTANT ===
Everything below is for Pica (picaos.com), your integration assistant that can instantly connect your AI agents to 100+ APIs.

Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC)

--- Tools Information ---
{ system_prompt }
"""
    prompt.strip()
    return prompt 