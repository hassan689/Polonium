"""
AI service for LLM interactions.
"""
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from datetime import datetime

from app.core.config import settings
from app.services.embedding_service import EmbeddingService


class AIService:
    """Service for AI/LLM interactions."""
    
    def __init__(self):
        """Initialize AI service with OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()
    
    async def generate_repository_overview(
        self,
        repository_name: str,
        file_summaries: List[Dict[str, Any]],
        existing_memories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI-powered repository overview.
        
        Args:
            repository_name: Name of the repository
            file_summaries: List of file summaries with paths and descriptions
            existing_memories: Optional existing memory chunks
            
        Returns:
            Dictionary with overview, architecture, tech_stack, and key_files
        """
        # Build context from file summaries
        file_context = "\n".join([
            f"- {f['path']}: {f.get('summary', 'No description')}"
            for f in file_summaries[:50]  # Limit to top 50 files
        ])
        
        memory_context = ""
        if existing_memories:
            memory_context = f"\n\nPrevious insights:\n" + "\n".join(existing_memories)
        
        prompt = f"""Analyze this GitHub repository: {repository_name}

Files in repository:
{file_context}
{memory_context}

Provide a comprehensive overview including:
1. What this repository does (overview)
2. High-level architecture description
3. Technology stack (programming languages, frameworks, tools)
4. Key files that are important to understand the codebase

Format your response as JSON with keys: overview, architecture, tech_stack (array), key_files (array of file paths)."""

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert software architect analyzing codebases. Provide clear, structured insights."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        return {
            "overview": result.get("overview", ""),
            "architecture": result.get("architecture"),
            "tech_stack": result.get("tech_stack", []),
            "key_files": result.get("key_files", []),
            "generated_at": datetime.utcnow(),
        }
    
    async def explain_file(
        self,
        file_path: str,
        file_content: str,
        repository_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI explanation for a file.
        
        Args:
            file_path: Path to the file
            file_content: Content of the file
            repository_context: Optional repository context
            
        Returns:
            Dictionary with explanation, purpose, key_functions, dependencies
        """
        context_section = ""
        if repository_context:
            context_section = f"\n\nRepository context:\n{repository_context}"
        
        # Truncate very long files
        max_content_length = 8000
        if len(file_content) > max_content_length:
            file_content = file_content[:max_content_length] + "\n\n[Content truncated...]"
        
        prompt = f"""Explain this file from a codebase:

File path: {file_path}
{context_section}

File content:
```{file_path.split('.')[-1] if '.' in file_path else ''}
{file_content}
```

Provide:
1. A clear explanation of what this file does
2. Its purpose in the codebase
3. Key functions/classes/exports (if applicable)
4. Dependencies or relationships with other files

Format as JSON with keys: explanation, purpose, key_functions (array), dependencies (array of file paths or module names)."""

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert code reviewer explaining code files clearly and concisely."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        return {
            "file_path": file_path,
            "explanation": result.get("explanation", ""),
            "purpose": result.get("purpose"),
            "key_functions": result.get("key_functions", []),
            "dependencies": result.get("dependencies", []),
            "generated_at": datetime.utcnow(),
        }
    
    async def generate_chat_response(
        self,
        user_message: str,
        repository_context: Optional[str] = None,
        relevant_files: Optional[List[Dict[str, Any]]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        memories: Optional[List[str]] = None,
    ) -> str:
        """
        Generate AI chat response with repository context.
        
        Args:
            user_message: User's message
            repository_context: Repository overview/context
            relevant_files: List of relevant files with content
            chat_history: Previous chat messages
            memories: Relevant memory chunks
            
        Returns:
            AI response text
        """
        system_prompt = """You are an AI assistant helping developers understand and work with a GitHub repository. 
You have access to the repository structure, files, and previous discussions. 
Provide helpful, accurate, and context-aware responses."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add repository context
        if repository_context:
            messages.append({
                "role": "system",
                "content": f"Repository context:\n{repository_context}",
            })
        
        # Add relevant memories
        if memories:
            messages.append({
                "role": "system",
                "content": f"Previous insights:\n" + "\n".join(memories),
            })
        
        # Add relevant files
        if relevant_files:
            files_context = "\n\nRelevant files:\n"
            for file_info in relevant_files[:5]:  # Limit to 5 files
                files_context += f"\n{file_info['path']}:\n{file_info.get('content', '')[:1000]}\n"
            messages.append({"role": "system", "content": files_context})
        
        # Add chat history
        if chat_history:
            for msg in chat_history[-10:]:  # Last 10 messages
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
        )
        
        return response.choices[0].message.content

