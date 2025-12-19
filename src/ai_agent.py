"""
AI Agent Module
Handles content generation using Google Gemini AI
"""

import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# LangChain imports with fallback
LANGCHAIN_AVAILABLE = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    try:
        from langchain.schema import HumanMessage, SystemMessage
    except ImportError:
        # Handle newer LangChain versions
        from langchain_core.messages import HumanMessage, SystemMessage
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.chains import LLMChain
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    print(f"LangChain import error (using direct Gemini): {e}")
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
        
        # Initialize text splitter
        if LANGCHAIN_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
        else:
            self.text_splitter = None
    
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
        """Summarize using LangChain"""
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPTS["summarization"]),
                ("human", f"""Please summarize the following text to approximately {target_length} words. 
                Focus on the main concepts, key points, and important details. 
                Maintain clarity and coherence while reducing length.
                
                Text to summarize:
                {{text}}
                
                Summary:""")
            ])
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = chain.run({"text": text})
            return result.strip()
        except Exception as e:
            print(f"LangChain summarization error: {e}")
            return self._simple_summary(text, 0.3)
    
    def _genai_summarize(self, text: str, target_length: int) -> str:
        """Summarize using direct Google GenerativeAI"""
        try:
            prompt = f"""Please summarize the following text to approximately {target_length} words. 
            Focus on the main concepts, key points, and important details. 
            Maintain clarity and coherence while reducing length.
            
            Text to summarize:
            {text}
            
            Summary:"""
            
            response = self.llm.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"GenAI summarization error: {e}")
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
        """Create outline using LangChain"""
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPTS["structuring"]),
                ("human", f"""Create a structured outline for a PowerPoint presentation based on the following text. 
                Generate a maximum of {max_slides} slides. Each slide should have:
                1. A clear, concise title
                2. A brief description of the content to include
                3. The type of slide (title, content, conclusion, etc.)
                
                Text content:
                {{text}}
                
                Return the outline as a JSON array with this structure:
                [
                    {{
                        "slide_number": 1,
                        "title": "Slide Title",
                        "content_type": "title/content/conclusion",
                        "content_description": "Brief description of what this slide should contain"
                    }}
                ]
                
                Outline:""")
            ])
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = chain.run({"text": text})
            
            # Parse JSON response
            try:
                outline = json.loads(result)
                if isinstance(outline, list):
                    return outline
            except json.JSONDecodeError:
                pass
            
            return self._create_fallback_outline(text, max_slides)
            
        except Exception as e:
            print(f"LangChain outline error: {e}")
            return self._create_fallback_outline(text, max_slides)
    
    def _genai_outline(self, text: str, max_slides: int) -> List[Dict[str, Any]]:
        """Create outline using direct Google GenerativeAI"""
        try:
            prompt = f"""Create a structured outline for a PowerPoint presentation based on the following text. 
            Generate a maximum of {max_slides} slides. For each slide, provide:
            1. A clear, concise title
            2. The type of slide (title, content, conclusion)
            3. A brief description of the content
            
            Text content:
            {text}
            
            Please format your response as a simple list, one slide per line:
            Slide 1: [Title] - [Type] - [Description]
            
            Outline:"""
            
            response = self.llm.generate_content(prompt)
            result = response.text.strip()
            
            # Parse the simple text response
            outline = []
            lines = result.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip() and ':' in line:
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
                            "slide_number": i + 1,
                            "title": title.strip(),
                            "content_type": content_type.strip(),
                            "content_description": description.strip()
                        })
            
            if outline:
                return outline
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
                return self._langchain_slide_content(title, content_type, content_description, original_text)
            elif self.use_genai:
                return self._genai_slide_content(title, content_type, content_description, original_text)
            else:
                return self._generate_fallback_slide_content(slide_info, original_text)
                
        except Exception as e:
            print(f"Error generating single slide content: {e}")
            return self._generate_fallback_slide_content(slide_info, original_text)
    
    def _genai_slide_content(self, title: str, content_type: str, content_description: str, original_text: str) -> Dict[str, Any]:
        """Generate slide content using direct Google GenerativeAI"""
        try:
            prompt = f"""Based on the original text and the slide information below, create detailed content for this slide.
                
                Slide Information:
                - Title: {title}
                - Content Type: {content_type}
                - Content Description: {content_description}
                
                Original Text:
                {original_text[:2000]}  # Limit text length
                
                Please create:
                1. 3-5 bullet points for this slide (each on a new line starting with •)
                2. Brief presenter notes (2-3 sentences)
                
                Format your response like this:
                BULLET POINTS:
                • First bullet point
                • Second bullet point
                • Third bullet point
                
                PRESENTER NOTES:
                Brief notes for the presenter here.
                
                Content:"""
            
            response = self.llm.generate_content(prompt)
            result = response.text.strip()
            
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
            
            return {
                "slide_number": slide_info.get("slide_number", 1),
                "title": title,
                "bullet_points": bullet_points if bullet_points else ["Content could not be generated"],
                "presenter_notes": presenter_notes if presenter_notes else f"This slide covers {title.lower()}. Please elaborate on the key points during your presentation."
            }
            
        except Exception as e:
            print(f"GenAI slide content error: {e}")
            return self._generate_fallback_slide_content(slide_info, original_text)
    
    def _langchain_slide_content(self, title: str, content_type: str, content_description: str, original_text: str) -> Dict[str, Any]:
        """Generate slide content using LangChain"""
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPTS["content_generation"]),
                ("human", f"""Based on the original text and the slide information below, create detailed content for this slide.
                
                Slide Information:
                - Title: {title}
                - Content Type: {content_type}
                - Content Description: {content_description}
                
                Original Text:
                {{original_text[:2000]}}  # Limit text length
                
                Please create:
                1. 3-5 bullet points for this slide (each on a new line starting with •)
                2. Brief presenter notes (2-3 sentences)
                
                Format your response like this:
                BULLET POINTS:
                • First bullet point
                • Second bullet point
                • Third bullet point
                
                PRESENTER NOTES:
                Brief notes for the presenter here.
                
                Content:""")
            ])
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = chain.run({"original_text": original_text})
            
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
            
            return {
                "slide_number": slide_info.get("slide_number", 1),
                "title": title,
                "bullet_points": bullet_points if bullet_points else ["Content could not be generated"],
                "presenter_notes": presenter_notes if presenter_notes else f"This slide covers {title.lower()}. Please elaborate on the key points during your presentation."
            }
            
        except Exception as e:
            print(f"LangChain slide content error: {e}")
            return self._generate_fallback_slide_content(slide_info, original_text)
    
    def _generate_fallback_slide_content(self, slide_info: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """Generate fallback slide content without AI"""
        title = slide_info.get("title", "Untitled Slide")
        content_desc = slide_info.get("content_description", "")
        
        # Extract relevant sentences from original text
        sentences = original_text.split('. ')
        relevant_sentences = []
        
        # Simple keyword matching to find relevant content
        title_words = title.lower().split()
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in title_words if len(word) > 3):
                relevant_sentences.append(sentence)
                if len(relevant_sentences) >= 3:
                    break
        
        # If no relevant sentences found, use first few sentences
        if not relevant_sentences:
            relevant_sentences = sentences[:3]
        
        # Create bullet points
        bullet_points = []
        for sentence in relevant_sentences[:5]:
            if sentence.strip():
                bullet_points.append(sentence.strip())
        
        # Create presenter notes
        presenter_notes = f"This slide covers {title.lower()}. "
        if content_desc:
            presenter_notes += f"Key points include: {content_desc}. "
        presenter_notes += "Please elaborate on these points during your presentation."
        
        return {
            "slide_number": slide_info.get("slide_number", 1),
            "title": title,
            "bullet_points": bullet_points if bullet_points else ["Content could not be generated"],
            "presenter_notes": presenter_notes
        }
    
    def _create_fallback_outline(self, text: str, max_slides: int) -> List[Dict[str, Any]]:
        """Create a basic outline if AI generation fails"""
        outline = []
        
        # Title slide
        outline.append({
            "slide_number": 1,
            "title": "Presentation Overview",
            "content_type": "title",
            "content_description": "Introduction to the presentation"
        })
        
        # Split text into sections
        paragraphs = text.split('\n\n')
        content_slides = min(max_slides - 2, len(paragraphs))
        
        for i in range(content_slides):
            if i < len(paragraphs):
                paragraph = paragraphs[i]
                # Create a title from first sentence
                title = paragraph.split('.')[0][:50] + "..." if len(paragraph.split('.')[0]) > 50 else paragraph.split('.')[0]
                
                outline.append({
                    "slide_number": i + 2,
                    "title": title,
                    "content_type": "content",
                    "content_description": paragraph[:200] + "..." if len(paragraph) > 200 else paragraph
                })
        
        # Conclusion slide
        if max_slides > 2:
            outline.append({
                "slide_number": len(outline) + 1,
                "title": "Conclusion",
                "content_type": "conclusion",
                "content_description": "Summary and key takeaways"
            })
        
        return outline
    
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
