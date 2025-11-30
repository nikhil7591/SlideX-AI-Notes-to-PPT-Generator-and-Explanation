"""
Explanation Agent Module for SlideX
Handles intelligent explanations for slide content
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
    print(f"LangChain import note in explanation agent (using direct Gemini): {e}")
    LANGCHAIN_AVAILABLE = False

# Direct Google AI import as fallback
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError as e:
    print(f"Google GenerativeAI import error in explanation agent: {e}")
    GENAI_AVAILABLE = False

# Local imports
from .config import Config, SYSTEM_PROMPTS

class ExplanationAgent:
    """Explanation Agent for providing intelligent explanations of slide content"""
    
    def __init__(self):
        """Initialize the explanation agent with Gemini"""
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
                    temperature=0.3,  # Lower temperature for more consistent explanations
                    google_api_key=self.config.GEMINI_API_KEY
                )
                print("Explanation Agent: LangChain Gemini initialized successfully")
                return llm
            elif GENAI_AVAILABLE:
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                model = genai.GenerativeModel(self.config.GEMINI_MODEL)
                print("Explanation Agent: Direct Gemini initialized successfully")
                return model
            else:
                raise Exception("Neither LangChain nor Google GenerativeAI is available")
        except Exception as e:
            print(f"Error initializing Explanation Agent LLM: {e}")
            return None
    
    def generate_slide_explanation(self, slide: Dict[str, Any], context: str = "", explanation_type: str = "Standard") -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a single slide with support for 'Standard' and 'Detailed' types.
        
        Args:
            slide: Slide dictionary with title, bullet_points, etc.
            context: Additional context from the original document
            explanation_type: Type of explanation ('Standard' or 'Detailed')
            
        Returns:
            Dictionary containing explanation components
        """
        try:
            if not self.llm:
                return self._generate_fallback_explanation(slide)
            
            title = slide.get("title", "Untitled Slide")
            bullet_points = slide.get("bullet_points", [])
            
            if self.use_langchain:
                return self._langchain_explanation(title, bullet_points, context, explanation_type)
            elif self.use_genai:
                return self._genai_explanation(title, bullet_points, context, explanation_type)
            else:
                return self._generate_fallback_explanation(slide)
                
        except Exception as e:
            print(f"Error generating slide explanation: {e}")
            return self._generate_fallback_explanation(slide)

    def _langchain_explanation(self, title: str, bullet_points: List[str], context: str, explanation_type: str) -> Dict[str, Any]:
        """Generate explanation using LangChain with support for explanation types."""
        # LangChain method delegates to genai_explanation to avoid complex import issues
        return self._genai_explanation(title, bullet_points, context, explanation_type)

    def _genai_explanation(self, title: str, bullet_points: List[str], context: str, explanation_type: str) -> Dict[str, Any]:
        """Generate explanation using direct Google GenerativeAI with support for explanation types."""
        try:
            bullet_text = "\n".join([f"• {point}" for point in bullet_points])
            
            prompt = f"""Generate a {explanation_type.lower()} explanation for the following slide content:
            
            Slide Title: {title}
            
            Bullet Points:
            {bullet_text}
            
            Additional Context:
            {context[:1000] if context else "No additional context provided"}
            
            Please provide the following in your response:
            
            EXPLANATION:
            [Detailed explanation of the slide content in 2-3 paragraphs]
            
            EXAMPLES:
            [2-3 real-world examples or analogies to help understand the concepts]
            
            KEY_TERMS:
            [List of important terms with brief definitions]
            
            QUESTIONS:
            [3-5 questions that might be asked about this content]
            
            RESOURCES:
            [Suggestions for further reading or resources]
            
            Format your response clearly with these section headers."""
            
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
            
            return self._parse_explanation_response(result)
            
        except Exception as e:
            print(f"GenAI explanation error: {e}")
            return self._generate_fallback_explanation({"title": title, "bullet_points": bullet_points})
    
    def _parse_explanation_response(self, response: str) -> Dict[str, Any]:
        """Parse the explanation response into structured components"""
        try:
            sections = {
                "explanation": "",
                "examples": [],
                "key_terms": [],
                "questions": [],
                "resources": []
            }
            
            lines = response.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('EXPLANATION:'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = "explanation"
                    current_content = []
                elif line.startswith('EXAMPLES:'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = "examples"
                    current_content = []
                elif line.startswith('KEY_TERMS:'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = "key_terms"
                    current_content = []
                elif line.startswith('QUESTIONS:'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = "questions"
                    current_content = []
                elif line.startswith('RESOURCES:'):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = "resources"
                    current_content = []
                elif line and current_section:
                    current_content.append(line)
            
            # Process the last section
            if current_section and current_content:
                content = '\n'.join(current_content).strip()
                if current_section == "examples":
                    sections["examples"] = [item.strip() for item in content.split('\n') if item.strip()]
                elif current_section == "key_terms":
                    sections["key_terms"] = [item.strip() for item in content.split('\n') if item.strip()]
                elif current_section == "questions":
                    sections["questions"] = [item.strip() for item in content.split('\n') if item.strip()]
                elif current_section == "resources":
                    sections["resources"] = [item.strip() for item in content.split('\n') if item.strip()]
                else:
                    sections[current_section] = content
            
            return sections
            
        except Exception as e:
            print(f"Error parsing explanation response: {e}")
            return {
                "explanation": response[:500] + "..." if len(response) > 500 else response,
                "examples": ["Example parsing failed"],
                "key_terms": ["Term parsing failed"],
                "questions": ["Question parsing failed"],
                "resources": ["Resource parsing failed"]
            }
    
    def _generate_fallback_explanation(self, slide: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback explanation with improved structure"""
        title = slide.get("title", "Untitled Slide")
        bullet_points = slide.get("bullet_points", [])
        
        bullet_text = "\n".join([f"• {point}" for point in bullet_points])
        
        return {
            "explanation": f"This slide, titled '{title}', highlights the following points: {bullet_text}. These points are crucial for understanding the topic.",
            "examples": [
                f"An example related to '{title}' could be a real-world scenario where these points are applied.",
                f"Consider how '{title}' impacts daily operations in a specific industry.",
                f"A case study illustrating '{title}' in action."
            ],
            "key_terms": [
                title,
                "Key concept derived from bullet points" if bullet_points else "Important terminology",
                "Relevant technical term"
            ],
            "questions": [
                f"Why is '{title}' significant?",
                "How can these points be applied practically?",
                "What challenges might arise from these concepts?",
                "What additional details could enhance understanding?",
                "How does this relate to the broader topic?"
            ],
            "resources": [
                "Recommended reading on related topics",
                "Guides or tutorials for deeper understanding",
                "Case studies or whitepapers on the subject"
            ]
        }
    
    def generate_presentation_summary(self, slides: List[Dict[str, Any]], original_context: str = "") -> Dict[str, Any]:
        """
        Generate a comprehensive summary for the entire presentation
        
        Args:
            slides: List of all slides in the presentation
            original_context: Original document context
            
        Returns:
            Dictionary containing presentation summary
        """
        try:
            if not self.llm:
                return self._generate_fallback_summary(slides)
            
            # Create a summary of slide titles and key points
            slide_summary = []
            for i, slide in enumerate(slides[:10]):  # Limit to first 10 slides for context
                title = slide.get("title", f"Slide {i+1}")
                bullet_points = slide.get("bullet_points", [])
                slide_summary.append(f"{i+1}. {title}: {', '.join(bullet_points[:2])}")
            
            slides_text = "\n".join(slide_summary)
            
            if self.use_langchain:
                return self._langchain_presentation_summary(slides_text, original_context)
            elif self.use_genai:
                return self._genai_presentation_summary(slides_text, original_context)
            else:
                return self._generate_fallback_summary(slides)
                
        except Exception as e:
            print(f"Error generating presentation summary: {e}")
            return self._generate_fallback_summary(slides)
    
    def _langchain_presentation_summary(self, slides_text: str, original_context: str) -> Dict[str, Any]:
        """Generate presentation summary using LangChain - delegates to genai method."""
        return self._genai_presentation_summary(slides_text, original_context)
    
    def _genai_presentation_summary(self, slides_text: str, original_context: str) -> Dict[str, Any]:
        """Generate presentation summary using direct Google GenerativeAI"""
        try:
            prompt = f"""Analyze the following presentation and provide a comprehensive summary:
            
            Presentation Slides:
            {slides_text}
            
            Original Context:
            {original_context[:1500] if original_context else "No original context provided"}
            
            Please provide:
            
            OVERVIEW:
            [A 2-3 paragraph overview of the entire presentation]
            
            KEY_TAKEAWAYS:
            [5-7 main takeaways from the presentation]
            
            AUDIENCE:
            [Description of the target audience and their knowledge level]
            
            PRESENTATION_TIPS:
            [3-4 tips for presenting this content effectively]
            
            Format your response clearly with these section headers."""
            
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
            
            return self._parse_summary_response(result)
            
        except Exception as e:
            print(f"GenAI presentation summary error: {e}")
            return self._generate_fallback_summary([])
    
    def _parse_summary_response(self, response: str) -> Dict[str, Any]:
        """Parse the presentation summary response"""
        try:
            sections = {
                "overview": "",
                "key_takeaways": [],
                "audience": "",
                "presentation_tips": []
            }
            
            lines = response.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('OVERVIEW:'):
                    if current_section and current_content:
                        content = '\n'.join(current_content).strip()
                        if current_section == "key_takeaways":
                            sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                        elif current_section == "presentation_tips":
                            sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                        else:
                            sections[current_section] = content
                    current_section = "overview"
                    current_content = []
                elif line.startswith('KEY_TAKEAWAYS:'):
                    if current_section and current_content:
                        content = '\n'.join(current_content).strip()
                        if current_section == "key_takeaways":
                            sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                        elif current_section == "presentation_tips":
                            sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                        else:
                            sections[current_section] = content
                    current_section = "key_takeaways"
                    current_content = []
                elif line.startswith('AUDIENCE:'):
                    if current_section and current_content:
                        content = '\n'.join(current_content).strip()
                        if current_section == "key_takeaways":
                            sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                        elif current_section == "presentation_tips":
                            sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                        else:
                            sections[current_section] = content
                    current_section = "audience"
                    current_content = []
                elif line.startswith('PRESENTATION_TIPS:'):
                    if current_section and current_content:
                        content = '\n'.join(current_content).strip()
                        if current_section == "key_takeaways":
                            sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                        elif current_section == "presentation_tips":
                            sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                        else:
                            sections[current_section] = content
                    current_section = "presentation_tips"
                    current_content = []
                elif line and current_section:
                    current_content.append(line)
            
            # Process the last section
            if current_section and current_content:
                content = '\n'.join(current_content).strip()
                if current_section == "key_takeaways":
                    sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                elif current_section == "presentation_tips":
                    sections[current_section] = [item.strip() for item in content.split('\n') if item.strip()]
                else:
                    sections[current_section] = content
            
            return sections
            
        except Exception as e:
            print(f"Error parsing summary response: {e}")
            return {
                "overview": "Summary parsing failed. Please review the presentation manually.",
                "key_takeaways": ["Takeaway parsing failed"],
                "audience": "Audience analysis failed",
                "presentation_tips": ["Tip parsing failed"]
            }
    
    def _generate_fallback_summary(self, slides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback presentation summary without AI"""
        slide_titles = [slide.get("title", f"Slide {i+1}") for i, slide in enumerate(slides)]
        
        return {
            "overview": f"This presentation covers {len(slides)} slides including: {', '.join(slide_titles[:5])}{'...' if len(slide_titles) > 5 else ''}. The content provides a comprehensive overview of the topic with structured information and key insights.",
            "key_takeaways": [
                f"Main concepts covered in {slide_titles[0] if slide_titles else 'the first slide'}",
                "Important relationships between topics",
                "Practical applications of the content",
                "Key insights and findings",
                "Summary of main points"
            ],
            "audience": "This presentation is suitable for professionals, students, or anyone interested in learning about the topic. No specialized prior knowledge is required.",
            "presentation_tips": [
                "Speak clearly and at a moderate pace",
                "Engage with your audience through questions",
                "Use visual aids to reinforce key points",
                "Allow time for questions and discussion"
            ]
        }
