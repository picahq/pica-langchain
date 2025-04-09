"""
System prompts for the Pica LangChain integration.
"""

from .default_system import get_default_system_prompt
from .authkit_system import get_authkit_system_prompt
from typing import Optional
import re

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
    
    # Extract supported connections from user_system_prompt if available
    supported_connections = None
    if user_system_prompt:
        # Look for <SUPPORTED CONNECTIONS> tag
        supported_connections_match = re.search(
            r'<SUPPORTED CONNECTIONS>(.*?)</SUPPORTED CONNECTIONS>', 
            user_system_prompt, 
            re.DOTALL
        )
        if supported_connections_match:
            supported_connections = supported_connections_match.group(1).strip()
            # Remove the tag from the user_system_prompt to avoid duplication
            user_system_prompt = re.sub(
                r'<SUPPORTED CONNECTIONS>.*?</SUPPORTED CONNECTIONS>', 
                '', 
                user_system_prompt, 
                flags=re.DOTALL
            ).strip()
    
    # If we found supported connections, inject them into the Pica system prompt
    if supported_connections:
        # Inject the supported connections into the IMPORTANT section of the system prompt
        system_prompt = re.sub(
            r'(IMPORTANT: When the user asks about "supported connections" or "available connections".*?DO NOT list all possible platforms if they\'re not in the active connections list\.)',
            r'\1\n\n' + supported_connections,
            system_prompt
        )
    
    prompt = f"""{ user_system_prompt or "" }
=== PICA: INTEGRATION ASSISTANT ===
Everything below is for Pica (picaos.com), your integration assistant that can instantly connect your AI agents to 100+ APIs.

Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC)

--- Tools Information ---
{ system_prompt }
"""
    prompt = prompt.strip()
    return prompt 