import re
from typing import List

from models.prompt_template import PromptTemplate

class PromptBuilder:
    """Service responsible for constructing prompts from templates."""
    
    @staticmethod
    def build(
        template: PromptTemplate, 
        task_title: str, 
        task_description: str, 
        chunks: List[str]
    ) -> str:
        """
        Constructs the final prompt string by injecting variables into the template.
        """
        context_str = "\n\n".join(chunks) if chunks else "No relevant context found."
        
        # Start with system prompt if available
        final_prompt = ""
        if template.system_prompt:
            final_prompt += template.system_prompt + "\n\n"
            
        # Replace variables in user prompt template
        user_prompt = template.user_prompt_template
        
        user_prompt = user_prompt.replace("{{task_title}}", task_title)
        user_prompt = user_prompt.replace("{{task_description}}", task_description)
        user_prompt = user_prompt.replace("{{retrieved_context}}", context_str)
        
        # Fallback for any unreplaced variables to avoid blowing up the LLM
        # This is optional, but good for robustness
        user_prompt = re.sub(r"\{\{.*?\}\}", "", user_prompt)
        
        final_prompt += user_prompt
        
        return final_prompt
