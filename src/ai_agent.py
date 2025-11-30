"""
AI Agent Module
Handles content generation using Google Gemini AI
"""

import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# LangChain imports with fallback - Simplified to use direct Gemini API
LANGCHAIN_AVAILABLE = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    print(f"LangChain import note (using direct Gemini): {e}")
    LANGCHAIN_AVAILABLE = False

# Direct Google AI import as fallback
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError as e:
    print(f"Google GenerativeAI import error: {e}")
    GENAI_AVAILABLE = False

# Local imports
from .config import Config, SYSTEM_PROMPTS

class AIAgent:
    """AI Agent for content generation using Google Gemini"""
    
    def __init__(self):
        """Initialize the AI agent with Gemini"""
        self.config = Config()
        self.llm = self._initialize_llm()
        self.use_langchain = LANGCHAIN_AVAILABLE
        self.use_genai = GENAI_AVAILABLE
    
    def _initialize_llm(self):
        """Initialize Gemini LLM with fallback"""
        try:
            if LANGCHAIN_AVAILABLE:
                llm = ChatGoogleGenerativeAI(
                    model=self.config.GEMINI_MODEL,
                    temperature=self.config.GEMINI_TEMPERATURE,
                    google_api_key=self.config.GEMINI_API_KEY
                )
                print("LangChain Gemini initialized successfully")
                return llm
            elif GENAI_AVAILABLE:
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                model = genai.GenerativeModel(self.config.GEMINI_MODEL)
                print("Direct Gemini initialized successfully")
                return model
            else:
                raise Exception("Neither LangChain nor Google GenerativeAI is available")
        except Exception as e:
            print(f"Error initializing Gemini LLM: {e}")
            return None
    
    def summarize_text(self, text: str, summary_ratio: float = 0.3) -> str:
        """
        Summarize the input text
        
        Args:
            text: Input text to summarize
            summary_ratio: Target summary length as ratio of original
            
        Returns:
            Summarized text
        """
        try:
            if not self.llm:
                return self._simple_summary(text, summary_ratio)
            
            target_length = max(100, int(len(text) * summary_ratio))
            
            if self.use_langchain:
                return self._langchain_summarize(text, target_length)
            elif self.use_genai:
                return self._genai_summarize(text, target_length)
            else:
                return self._simple_summary(text, summary_ratio)
                
        except Exception as e:
            print(f"Error in text summarization: {e}")
            return self._simple_summary(text, summary_ratio)
    
    def _langchain_summarize(self, text: str, target_length: int) -> str:
        """Summarize using LangChain - delegates to genai method"""
        return self._genai_summarize(text, target_length)
    
    def _genai_summarize(self, text: str, target_length: int) -> str:
        """Summarize using direct Google GenerativeAI or LangChain"""
        try:
            prompt = f"""Please summarize the following text to approximately {target_length} words. 
            Focus on the main concepts, key points, and important details. 
            Maintain clarity and coherence while reducing length.
            
            Text to summarize:
            {text}
            
            Summary:"""
            
            # Try LangChain method first
            if self.use_langchain and hasattr(self.llm, 'invoke'):
                from langchain_core.messages import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content.strip() if hasattr(response, 'content') else str(response).strip()
            elif self.use_genai and hasattr(self.llm, 'generate_content'):
                response = self.llm.generate_content(prompt)
                return response.text.strip()
            else:
                # Fallback
                return self._simple_summary(text, 0.3)
        except Exception as e:
            print(f"Summarization error: {e}")
            return self._simple_summary(text, 0.3)
    
    def _simple_summary(self, text: str, summary_ratio: float) -> str:
        """Simple text summarization without AI"""
        if not text:
            return ""
        
        # Split into sentences
        sentences = text.split('. ')
        target_length = max(2, int(len(sentences) * summary_ratio))
        
        # Take first few sentences
        summary = '. '.join(sentences[:target_length])
        
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary.strip()
    
    def create_slide_outline(self, summarized_text: str, max_slides: int = 20) -> List[Dict[str, Any]]:
        """
        Create a structured outline for slides
        
        Args:
            summarized_text: Summarized content
            max_slides: Maximum number of slides to create
            
        Returns:
            List of slide outlines with titles and content descriptions
        """
        try:
            if not self.llm:
                return self._create_fallback_outline(summarized_text, max_slides)
                
            if self.use_langchain:
                return self._langchain_outline(summarized_text, max_slides)
            elif self.use_genai:
                return self._genai_outline(summarized_text, max_slides)
            else:
                return self._create_fallback_outline(summarized_text, max_slides)
                
        except Exception as e:
            print(f"Error creating slide outline: {e}")
            return self._create_fallback_outline(summarized_text, max_slides)
    
    def generate_slide_outline(self, text: str, max_slides: int = 20) -> List[Dict[str, Any]]:
        """
        Generate a structured outline for slides (alias for create_slide_outline)
        
        Args:
            text: Content to create outline from
            max_slides: Maximum number of slides to create
            
        Returns:
            List of slide outlines with titles and content descriptions
        """
        # First summarize the text for better outline generation
        summarized = self.summarize_text(text, summary_ratio=0.4)
        return self.create_slide_outline(summarized, max_slides)
    
    def _langchain_outline(self, text: str, max_slides: int) -> List[Dict[str, Any]]:
        """Create outline using LangChain - delegates to genai for compatibility."""
        return self._genai_outline(text, max_slides)
    
    def _genai_outline(self, text: str, max_slides: int) -> List[Dict[str, Any]]:
        """Create outline using direct Google GenerativeAI with max_slides enforcement."""
        try:
            prompt = f"""Create a structured outline for a PowerPoint presentation based on the following text. 
            Generate EXACTLY {max_slides} slides (no more, no less). Each slide should have:
            1. A clear, concise, short title (5-8 words max)
            2. The type of slide (title, content, conclusion)
            
            Text content:
            {text[:2000]}
            
            IMPORTANT:
            - NO examples, NO expected questions, NO definitions
            - Keep titles SHORT and CRISP
            - Focus on KEY CONCEPTS only
            - Generate exactly {max_slides} slides
            
            Format your response as:
            Slide 1: [Short Title] - [Type]
            Slide 2: [Short Title] - [Type]
            
            Outline:"""
            
            # Use proper LLM call method
            if hasattr(self.llm, 'invoke'):
                from langchain_core.messages import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                result = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            elif hasattr(self.llm, 'generate_content'):
                response = self.llm.generate_content(prompt)
                result = response.text.strip()
            else:
                result = str(self.llm(prompt))
            
            # Parse the simple text response
            outline = []
            lines = result.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip() and ':' in line and len(outline) < max_slides:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        content = parts[1].strip()
                        if ' - ' in content:
                            title, rest = content.split(' - ', 1)
                            if ' - ' in rest:
                                content_type, description = rest.split(' - ', 1)
                            else:
                                content_type = "content"
                                description = rest
                        else:
                            title = content
                            content_type = "content"
                            description = ""
                        
                        outline.append({
                            "slide_number": len(outline) + 1,
                            "title": title.strip(),
                            "content_type": content_type.strip(),
                            "content_description": description.strip()
                        })
            
            # Ensure we have the requested number of slides
            if len(outline) < max_slides:
                remaining = max_slides - len(outline)
                fallback_outline = self._create_fallback_outline(text, remaining)
                for i, slide in enumerate(fallback_outline):
                    slide["slide_number"] = len(outline) + i + 1
                outline.extend(fallback_outline)
            
            if outline:
                return outline[:max_slides]
            else:
                return self._create_fallback_outline(text, max_slides)
            
        except Exception as e:
            print(f"GenAI outline error: {e}")
            return self._create_fallback_outline(text, max_slides)
    
    def generate_slide_content(self, slide_outline: List[Dict[str, Any]], original_text: str) -> List[Dict[str, Any]]:
        """
        Generate detailed content for each slide
        
        Args:
            slide_outline: List of slide outlines
            original_text: Original text for reference
            
        Returns:
            List of slides with bullet points and presenter notes
        """
        slides = []
        
        for slide_info in slide_outline:
            try:
                if self.llm and (self.use_langchain or self.use_genai):
                    slide_content = self._generate_single_slide_content(slide_info, original_text)
                else:
                    slide_content = self._generate_fallback_slide_content(slide_info, original_text)
                slides.append(slide_content)
            except Exception as e:
                print(f"Error generating content for slide {slide_info.get('slide_number', 'unknown')}: {e}")
                # Add fallback slide
                slides.append({
                    "slide_number": slide_info.get("slide_number", len(slides) + 1),
                    "title": slide_info.get("title", "Slide"),
                    "bullet_points": ["Content generation failed"],
                    "presenter_notes": "Please check the original document for this content."
                })
        
        return slides
    
    def _generate_single_slide_content(self, slide_info: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Generate content for a single slide"""
        try:
            title = slide_info.get("title", "Untitled Slide")
            content_type = slide_info.get("content_type", "content")
            content_description = slide_info.get("content_description", "")
            
            if self.use_langchain:
                return self._langchain_slide_content(title, content_type, content_description, original_text, slide_info)
            elif self.use_genai:
                return self._genai_slide_content(title, content_type, content_description, original_text, slide_info)
            else:
                return self._generate_fallback_slide_content(slide_info, original_text)
                
        except Exception as e:
            print(f"Error generating single slide content: {e}")
            return self._generate_fallback_slide_content(slide_info, original_text)
    
    def _langchain_slide_content(self, title: str, content_type: str, content_description: str, original_text: str, slide_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate slide content using LangChain - delegates to genai for compatibility."""
        return self._genai_slide_content(title, content_type, content_description, original_text, slide_info)
    
    def _genai_slide_content(self, title: str, content_type: str, content_description: str, original_text: str, slide_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate slide content using direct Google GenerativeAI with unique, crisp content per slide"""
        try:
            slide_num = slide_info.get("slide_number", 1) if slide_info else 1
            
            prompt = f"""Based on the original text, create CRISP and UNIQUE content for this slide (Slide {slide_num}).

Slide Title: {title}
Slide Number: {slide_num}

Original Text:
{original_text[:2500]}

IMPORTANT INSTRUCTIONS:
- Create POINT-TO-POINT, CRISP bullet points (not examples, not explanations)
- Each bullet should be 1-2 lines maximum
- DIFFERENT content for each slide - NO REPETITION
- Focus on KEY FACTS and KEY CONCEPTS
- NO examples, NO expected questions, NO definitions
- Create exactly 4-5 unique bullet points
- Keep presenter notes SHORT (1-2 sentences max)

Format response EXACTLY as:
BULLET POINTS:
• First crisp key point
• Second crisp key point
• Third crisp key point

PRESENTER NOTES:
One sentence presenter note.

Content:"""
            
            # Use proper LLM call method
            if hasattr(self.llm, 'invoke'):
                from langchain_core.messages import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                result = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            elif hasattr(self.llm, 'generate_content'):
                response = self.llm.generate_content(prompt)
                result = response.text.strip()
            else:
                result = str(self.llm(prompt))
            
            # Parse the response
            bullet_points = []
            presenter_notes = ""
            
            lines = result.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('BULLET POINTS:'):
                    current_section = 'bullets'
                elif line.startswith('PRESENTER NOTES:'):
                    current_section = 'notes'
                elif line.startswith('•') and current_section == 'bullets':
                    bullet_points.append(line[1:].strip())
                elif line and current_section == 'notes' and not line.startswith('PRESENTER'):
                    presenter_notes += line + " "
            
            # Clean up presenter notes
            presenter_notes = presenter_notes.strip()
            
            if slide_info is None:
                slide_info = {}
            
            return {
                "slide_number": slide_info.get("slide_number", 1),
                "title": title,
                "bullet_points": bullet_points if bullet_points else ["Content could not be generated"],
                "presenter_notes": presenter_notes if presenter_notes else f"This slide covers {title.lower()}. Please elaborate on the key points during your presentation.",
                "content_type": content_type
            }
            
        except Exception as e:
            print(f"GenAI slide content error: {e}")
            return self._generate_fallback_slide_content(slide_info if slide_info else {}, original_text)
    
    def _generate_fallback_slide_content(self, slide_info: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Generate fallback slide content with crisp, unique points per slide"""
        title = slide_info.get("title", "Untitled Slide")
        slide_num = slide_info.get("slide_number", 1)
        
        # Extract relevant sentences from original text
        sentences = [s.strip() for s in original_text.split('. ') if s.strip() and len(s.strip()) > 10]
        
        # Get unique bullet points for this slide based on slide number
        bullet_points = []
        
        if sentences:
            # Rotate through sentences to get different content per slide
            start_idx = ((slide_num - 1) * 4) % len(sentences)
            for i in range(5):
                idx = (start_idx + i) % len(sentences)
                sentence = sentences[idx].strip()
                
                # Make it crisp - take first part of sentence
                if len(sentence) > 80:
                    # Extract key phrase from sentence
                    parts = sentence.split(',')
                    crisp_point = parts[0].strip()
                    if len(crisp_point) > 100:
                        crisp_point = crisp_point[:95] + "..."
                else:
                    crisp_point = sentence
                
                if crisp_point not in bullet_points:
                    bullet_points.append(crisp_point)
        
        # If not enough bullets, generate generic but unique ones
        if len(bullet_points) < 4:
            for i in range(4):
                bullet_points.append(f"Key concept {slide_num}.{i+1}")
        
        # Short presenter notes - 1-2 sentences max
        presenter_notes = f"Slide {slide_num}: {title}. Focus on the key points listed above."
        
        return {
            "slide_number": slide_num,
            "title": title,
            "bullet_points": bullet_points[:5],
            "presenter_notes": presenter_notes
        }
    
    def _create_fallback_outline(self, text: str, max_slides: int) -> List[Dict[str, Any]]:
        """Create a comprehensive outline with focused, crisp titles"""
        try:
            outline = []
            
            # Split text into sections and paragraphs for variety
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            sentences = [s.strip() for s in text.split('. ') if s.strip() and len(s.strip()) > 15]
            
            # Generate exactly max_slides slides with diverse content
            for i in range(max_slides):
                # Rotate through different text sources for variety
                if i < len(paragraphs):
                    # Use paragraph-based content - extract crisp title
                    para = paragraphs[i]
                    title_text = para.split('.')[0] if '.' in para else para
                    title = title_text[:55].strip()
                    if not title or len(title) < 5:
                        title = f"Topic {i + 1}"
                    description = para[:200]
                    
                elif i < len(sentences):
                    # Use sentence-based content
                    sent_idx = min(i, len(sentences) - 1)
                    sent = sentences[sent_idx]
                    # Extract crisp title from sentence
                    if len(sent) > 60:
                        title = sent[:55] + "..."
                    else:
                        title = sent
                    description = sent[:200]
                else:
                    # Generic slides with unique numbering
                    title = f"Key Point {i + 1}"
                    description = f"Important information related to section {i + 1}"
                
                outline.append({
                    "slide_number": i + 1,
                    "title": title,
                    "content_type": "content",
                    "content_description": description
                })
            
            return outline
        
        except Exception as e:
            print(f"Error in fallback outline: {e}")
            # Return generic slides as last resort
            fallback = []
            for i in range(max_slides):
                fallback.append({
                    "slide_number": i + 1,
                    "title": f"Point {i + 1}",
                    "content_type": "content",
                    "content_description": f"Content {i + 1}"
                })
            return fallback
    
    def process_document(self, text: str, max_slides: int = 20) -> Dict[str, Any]:
        """
        Complete document processing pipeline
        
        Args:
            text: Input document text
            max_slides: Maximum number of slides to generate
            
        Returns:
            Dictionary containing processed content
        """
        try:
            print(f"Starting document processing with {len(text)} characters")
            
            # Step 1: Summarize the text
            print("Step 1: Summarizing text...")
            summarized_text = self.summarize_text(text)
            print(f"Summarized text length: {len(summarized_text)}")
            
            # Step 2: Create slide outline
            print("Step 2: Creating slide outline...")
            slide_outline = self.create_slide_outline(summarized_text, max_slides)
            print(f"Created outline with {len(slide_outline)} slides")
            
            # Step 3: Generate detailed slide content
            print("Step 3: Generating slide content...")
            slides = self.generate_slide_content(slide_outline, text)
            print(f"Generated content for {len(slides)} slides")
            
            return {
                "success": True,
                "original_text_length": len(text),
                "summarized_text_length": len(summarized_text),
                "slide_count": len(slides),
                "slides": slides,
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in document processing: {e}")
            # Return a basic presentation even if everything fails
            return self._create_emergency_presentation(text, max_slides)
    
    def _create_fallback_outline(self, text: str, max_slides: int) -> List[Dict[str, Any]]:
        """Create a simple fallback outline without AI"""
        try:
            # Split text into sections
            sentences = text.split('. ')
            outline = []
            
            # Title slide
            outline.append({
                "slide_number": 1,
                "title": "Document Overview",
                "content_type": "title",
                "content_description": "Introduction to the document content"
            })
            
            # Content slides
            num_content_slides = min(max_slides - 2, max(3, len(sentences) // 5))
            
            for i in range(num_content_slides):
                outline.append({
                    "slide_number": i + 2,
                    "title": f"Content Section {i + 1}",
                    "content_type": "content",
                    "content_description": f"Key points from section {i + 1}"
                })
            
            # Conclusion slide
            outline.append({
                "slide_number": len(outline) + 1,
                "title": "Conclusion",
                "content_type": "conclusion",
                "content_description": "Summary and closing remarks"
            })
            
            return outline
            
        except Exception as e:
            print(f"Error in fallback outline: {e}")
            return [{"slide_number": 1, "title": "Presentation", "content_type": "title", "content_description": "Basic presentation"}]
    
    def _create_emergency_presentation(self, text: str, max_slides: int) -> Dict[str, Any]:
        try:
            print("Creating emergency presentation...")
            
            # Split text into basic sections
            sentences = text.split('. ')
            slides = []
            
            # Title slide
            slides.append({
                "slide_number": 1,
                "title": "Document Overview",
                "bullet_points": ["Generated from uploaded document", f"Document length: {len(text)} characters"],
                "presenter_notes": "This presentation was generated from an uploaded document. Please review the content and customize as needed."
            })
            
            # Content slides
            num_content_slides = min(max_slides - 2, max(3, len(sentences) // 5))
            
            for i in range(num_content_slides):
                start_idx = i * 5
                end_idx = min(start_idx + 5, len(sentences))
                content_sentences = sentences[start_idx:end_idx]
                
                if content_sentences:
                    bullet_points = []
                    for sentence in content_sentences:
                        if sentence.strip():
                            bullet_points.append(sentence.strip())
                    
                    slides.append({
                        "slide_number": i + 2,
                        "title": f"Content Section {i + 1}",
                        "bullet_points": bullet_points[:5],  # Max 5 bullet points
                        "presenter_notes": f"This section covers key points from the document. Please elaborate on each bullet point during your presentation."
                    })
            
            # Conclusion slide
            slides.append({
                "slide_number": len(slides) + 1,
                "title": "Conclusion",
                "bullet_points": ["End of presentation", "Thank you for your attention"],
                "presenter_notes": "This concludes the presentation. Please feel free to ask any questions."
            })
            
            return {
                "success": True,
                "original_text_length": len(text),
                "summarized_text_length": len(text),
                "slide_count": len(slides),
                "slides": slides,
                "processing_time": datetime.now().isoformat(),
                "fallback_used": True
            }
            
        except Exception as e:
            print(f"Error in emergency presentation: {e}")
            return {
                "success": False,
                "error": str(e),
                "slides": []
            }
