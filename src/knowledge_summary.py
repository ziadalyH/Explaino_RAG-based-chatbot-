"""Knowledge summary generator for RAG system."""

import logging
import json
from pathlib import Path
from typing import List, Dict
import openai

from .config import Config


class KnowledgeSummaryGenerator:
    """
    Generates summaries of indexed content and suggested questions.
    """
    
    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialize the knowledge summary generator.
        
        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.summary_file = Path("data/knowledge_summary.json")
        
        # Initialize OpenAI
        if config.openai_api_key:
            openai.api_key = config.openai_api_key
    
    def generate_summary(
        self,
        pdf_files: List[str],
        video_ids: List[str],
        sample_chunks: Dict[str, List[str]]
    ) -> Dict:
        """
        Generate a knowledge summary from indexed content.
        
        Args:
            pdf_files: List of PDF filenames
            video_ids: List of video IDs
            sample_chunks: Sample text chunks from PDFs and videos
            
        Returns:
            Dictionary with summary and suggested questions
        """
        self.logger.info("Generating knowledge summary...")
        
        # Build context for LLM
        context = self._build_context(pdf_files, video_ids, sample_chunks)
        
        # Generate summary with LLM
        summary_data = self._generate_with_llm(context)
        
        # Save to file
        self._save_summary(summary_data)
        
        self.logger.info("Knowledge summary generated successfully")
        return summary_data
    
    def _build_context(
        self,
        pdf_files: List[str],
        video_ids: List[str],
        sample_chunks: Dict[str, List[str]]
    ) -> str:
        """Build context string for LLM."""
        context_parts = []
        
        # Add PDF information
        if pdf_files:
            context_parts.append(f"PDF Documents ({len(pdf_files)}):")
            for pdf in pdf_files[:10]:  # Limit to first 10
                context_parts.append(f"  - {pdf}")
            if len(pdf_files) > 10:
                context_parts.append(f"  ... and {len(pdf_files) - 10} more")
        
        # Add video information
        if video_ids:
            context_parts.append(f"\nVideo Transcripts ({len(video_ids)}):")
            for vid in video_ids[:10]:  # Limit to first 10
                context_parts.append(f"  - {vid}")
            if len(video_ids) > 10:
                context_parts.append(f"  ... and {len(video_ids) - 10} more")
        
        # Add sample content
        if sample_chunks.get('pdf'):
            context_parts.append("\nSample PDF Content:")
            for chunk in sample_chunks['pdf'][:5]:
                context_parts.append(f"  - {chunk[:200]}...")
        
        if sample_chunks.get('video'):
            context_parts.append("\nSample Video Content:")
            for chunk in sample_chunks['video'][:5]:
                context_parts.append(f"  - {chunk[:200]}...")
        
        return "\n".join(context_parts)
    
    def _generate_with_llm(self, context: str) -> Dict:
        """Generate summary using LLM."""
        prompt = f"""Based on the following indexed content, generate a comprehensive knowledge summary and suggested questions.

{context}

Please provide:
1. A brief overview of the main topics covered (2-3 sentences)
2. A list of 5-10 key topics/subjects
3. 8-12 example questions users can ask

Format your response as JSON:
{{
  "overview": "Brief overview text...",
  "topics": ["Topic 1", "Topic 2", ...],
  "suggested_questions": [
    "Question 1?",
    "Question 2?",
    ...
  ]
}}"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that analyzes document collections and generates summaries. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse JSON response
            content = response['choices'][0]['message']['content'].strip()
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            summary_data = json.loads(content)
            
            # Validate structure
            if not all(key in summary_data for key in ['overview', 'topics', 'suggested_questions']):
                raise ValueError("Invalid summary structure")
            
            return summary_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary with LLM: {e}")
            # Return fallback summary
            return {
                "overview": "This knowledge base contains various documents and videos on multiple topics.",
                "topics": ["General Knowledge"],
                "suggested_questions": [
                    "What topics are covered in this knowledge base?",
                    "Can you summarize the main content?",
                    "What information is available?"
                ]
            }
    
    def _save_summary(self, summary_data: Dict):
        """Save summary to file."""
        try:
            # Ensure data directory exists
            self.summary_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as JSON
            with open(self.summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2)
            
            self.logger.info(f"Summary saved to {self.summary_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save summary: {e}")
    
    def load_summary(self) -> Dict:
        """
        Load existing summary from file.
        
        Returns:
            Dictionary with summary data, or None if not found
        """
        try:
            if self.summary_file.exists():
                with open(self.summary_file, 'r') as f:
                    return json.load(f)
            else:
                self.logger.warning("No summary file found")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to load summary: {e}")
            return None
