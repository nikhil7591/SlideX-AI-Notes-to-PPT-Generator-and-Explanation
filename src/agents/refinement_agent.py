"""
Refinement Agent
Improves clarity, consistency, and presentation quality of generated slides
"""

from typing import List, Dict, Any, Optional
import json
import re

# LLM imports
LANGCHAIN_AVAILABLE = False
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    try:
        from langchain.schema import HumanMessage, SystemMessage
    except ImportError:
        from langchain_core.messages import HumanMessage, SystemMessage
    from langchain.prompts import ChatPromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from ..config import Config


class RefinementAgent:
    """
    Agent responsible for refining slide content.
    Ensures:
    - Clarity and readability
    - Consistency across slides
    - Presentation quality
    - Proper formatting
    - No duplicate content
    """
    
    def __init__(self):
        self.config = Config()
        self.llm = self._initialize_llm()
        self.use_langchain = LANGCHAIN_AVAILABLE
        self.use_genai = GENAI_AVAILABLE
    
    def _initialize_llm(self):
        """Initialize LLM for refinement"""
        try:
            if LANGCHAIN_AVAILABLE:
                return ChatGoogleGenerativeAI(
                    model=self.config.GEMINI_MODEL,
                    temperature=0.4,  # Lower temperature for more focused refinement
                    google_api_key=self.config.GEMINI_API_KEY
                )
            elif GENAI_AVAILABLE:
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                return genai.GenerativeModel(self.config.GEMINI_MODEL)
            else:
                return None
        except Exception as e:
            print(f"Error initializing Refinement Agent LLM: {e}")
            return None
    
    def refine_slides(
        self,
        slides: List[Dict[str, Any]],
        template_style: str = "modern",
        explanation_level: str = "standard"
    ) -> List[Dict[str, Any]]:
        """
        Refine all slides for clarity, consistency, and quality
        
        Args:
            slides: List of generated slides
            template_style: Template style (modern, academic)
            explanation_level: Explanation level (standard, detailed)
            
        Returns:
            List of refined slides
        """
        try:
            if not slides:
                return []
            
            if not self.llm:
                return self._fallback_refinement(slides)
            
            # Check for consistency and duplicates
            refined_slides = []
            
            for i, slide in enumerate(slides):
                # Refine individual slide
                refined_slide = self.refine_single_slide(
                    slide,
                    slides,  # Pass all slides for context
                    template_style,
                    explanation_level
                )
                refined_slides.append(refined_slide)
            
            # Final consistency check across all slides
            refined_slides = self._ensure_consistency(refined_slides)
            
            return refined_slides
            
        except Exception as e:
            print(f"Error refining slides: {e}")
            return self._fallback_refinement(slides)
    
    def refine_single_slide(
        self,
        slide: Dict[str, Any],
        all_slides: List[Dict[str, Any]],
        template_style: str,
        explanation_level: str
    ) -> Dict[str, Any]:
        """Refine a single slide"""
        try:
            if not self.llm:
                return self._fallback_refine_single(slide)
            
            # Check for obvious issues first
            title = slide.get("title", "Untitled")
            bullet_points = slide.get("bullet_points", [])
            
            # Quick checks
            if not title or title.lower() in ["untitled", "slide", "title"]:
                # Generate better title from content
                if bullet_points:
                    title = self._generate_title_from_content(bullet_points[0])
                    slide["title"] = title
            
            if not bullet_points:
                return slide  # Skip if no content
            
            # Use LLM for detailed refinement
            if self.use_langchain:
                return self._langchain_refine_slide(slide, all_slides, template_style, explanation_level)
            elif self.use_genai:
                return self._genai_refine_slide(slide, all_slides, template_style, explanation_level)
            else:
                return self._fallback_refine_single(slide)
                
        except Exception as e:
            print(f"Error refining single slide: {e}")
            return self._fallback_refine_single(slide)
    
    def _langchain_refine_slide(
        self,
        slide: Dict[str, Any],
        all_slides: List[Dict[str, Any]],
        template_style: str,
        explanation_level: str
    ) -> Dict[str, Any]:
        """Refine slide using LangChain"""
        try:
            title = slide.get("title", "Untitled")
            bullet_points = slide.get("bullet_points", [])
            slide_num = slide.get("slide_number", 1)
            
            # Get context from other slides
            other_titles = [s.get("title", "") for s in all_slides if s.get("slide_number") != slide_num]
            
            bullets_text = "\n".join([f"• {bp}" for bp in bullet_points])
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert presentation editor. Your task is to refine slide content for:
1. Clarity and readability
2. Consistency with other slides
3. Presentation quality
4. Proper formatting
5. Avoiding generic or duplicate content
6. Ensuring UNIQUE topics per slide (NO repetition)
7. Removing numeric headings like (1), (2), (3)
8. Ensuring each title is unique and meaningful

CRITICAL ANTI-REPETITION RULES:
- Check if content has been used in previous slides - if yes, remove it
- Ensure each slide title is UNIQUE (no duplicates)
- Remove any numeric prefixes or auto-numbering from titles
- Ensure each slide covers a DIFFERENT topic

Improve the content while maintaining the original meaning and intent, but prioritize uniqueness and non-repetition."""),
                ("human", f"""Refine this slide content for clarity, consistency, and quality:

Current Title: {title}
Current Bullet Points:
{bullets_text}

Other Slide Titles (for consistency check):
{', '.join(other_titles[:5])}

Template Style: {template_style}
- Modern: concise, impactful, minimal
- Academic: formal, structured, clear

Refine the title and bullet points. Ensure:
- Title is UNIQUE and meaningful (not generic, NO numbering like (1), (2), NO repeated titles)
- Bullet points are clear and concise
- NO redundancy or duplication with other slides
- Consistent tone with template style
- Content is specific to THIS topic only (no repeated introductory or general content)
- Check against other slide titles - must be DIFFERENT

Format response as:
REFINED_TITLE:
[Improved title]

REFINED_BULLETS:
• [Improved bullet 1]
• [Improved bullet 2]
...

Refined Content:""")
            ])
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = chain.run({})
            
            # Parse refined content
            return self._parse_refined_content(result, slide)
            
        except Exception as e:
            print(f"LangChain refinement error: {e}")
            return self._fallback_refine_single(slide)
    
    def _genai_refine_slide(
        self,
        slide: Dict[str, Any],
        all_slides: List[Dict[str, Any]],
        template_style: str,
        explanation_level: str
    ) -> Dict[str, Any]:
        """Refine slide using direct GenAI"""
        try:
            title = slide.get("title", "Untitled")
            bullet_points = slide.get("bullet_points", [])
            slide_num = slide.get("slide_number", 1)
            
            other_titles = [s.get("title", "") for s in all_slides if s.get("slide_number") != slide_num]
            bullets_text = "\n".join([f"• {bp}" for bp in bullet_points])
            
            prompt = f"""Refine this slide for clarity, consistency, and quality:

Title: {title}
Bullets:
{bullets_text}

Other Titles: {', '.join(other_titles[:5])}
Style: {template_style}

Refine title and bullets. Ensure uniqueness, clarity, and consistency.

REFINED_TITLE:
[Title]

REFINED_BULLETS:
• [Bullet 1]
• [Bullet 2]
...

Refined Content:"""
            
            response = self.llm.generate_content(prompt)
            result = response.text.strip()
            
            return self._parse_refined_content(result, slide)
            
        except Exception as e:
            print(f"GenAI refinement error: {e}")
            return self._fallback_refine_single(slide)
    
    def _parse_refined_content(self, response: str, original_slide: Dict[str, Any]) -> Dict[str, Any]:
        """Parse refined content from LLM response"""
        title = original_slide.get("title", "Untitled")
        bullet_points = original_slide.get("bullet_points", [])
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('REFINED_TITLE:'):
                current_section = 'title'
            elif line.startswith('REFINED_BULLETS:'):
                current_section = 'bullets'
            elif line and current_section == 'title':
                title_text = line.replace('REFINED_TITLE:', '').strip()
                # Remove numeric prefixes
                title_text = re.sub(r'^\(\d+\)\s*', '', title_text)
                title_text = re.sub(r'^\d+\.\s*', '', title_text)
                title_text = re.sub(r'^Slide\s+\d+:\s*', '', title_text, flags=re.IGNORECASE)
                if title_text:
                    title = title_text
                current_section = None
            elif line and current_section == 'bullets':
                bullet_text = line.strip()
                bullet_text = re.sub(r'^[•\-\*]\s*', '', bullet_text)
                if bullet_text:
                    bullet_points.append(bullet_text)
        
        # If parsing failed, keep original
        if not bullet_points:
            bullet_points = original_slide.get("bullet_points", [])
        
        # Final cleanup: remove numeric prefixes from title if not already cleaned
        title = re.sub(r'^\(\d+\)\s*', '', title)
        title = re.sub(r'^\d+\.\s*', '', title)
        title = re.sub(r'^Slide\s+\d+:\s*', '', title, flags=re.IGNORECASE)
        
        return {
            **original_slide,
            "title": title.strip(),
            "bullet_points": bullet_points[:8]  # Limit bullets
        }
    
    def _ensure_consistency(self, slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure consistency across all slides and remove duplicates"""
        # Check for duplicate titles and remove numeric prefixes
        seen_titles = set()
        title_counts = {}
        
        # First pass: clean titles and identify duplicates
        for slide in slides:
            title = slide.get("title", "").strip()
            # Remove numeric prefixes like "(1) ", "1. ", etc.
            title = re.sub(r'^\(\d+\)\s*', '', title)  # Remove (1), (2), etc.
            title = re.sub(r'^\d+\.\s*', '', title)  # Remove 1., 2., etc.
            title = re.sub(r'^Slide\s+\d+:\s*', '', title, flags=re.IGNORECASE)  # Remove "Slide 1:"
            slide["title"] = title
            if title:
                title_counts[title] = title_counts.get(title, 0) + 1
        
        # Fix duplicate titles by making them unique with topic-specific variations
        for slide in slides:
            title = slide.get("title", "")
            if title_counts.get(title, 0) > 1 and title in seen_titles:
                # Generate alternative title based on content
                bullet_points = slide.get("bullet_points", [])
                if bullet_points:
                    # Try to derive unique title from first bullet
                    new_title = self._generate_unique_title_from_content(bullet_points[0], seen_titles)
                    slide["title"] = new_title
                    seen_titles.add(new_title)
                    title_counts[title] -= 1
                else:
                    # Fallback: use slide number but make it meaningful
                    slide_num = slide.get("slide_number", "")
                    if slide_num and slide_num > 1:
                        slide["title"] = f"Topic {slide_num}"
                if title in seen_titles:
                    title_counts[title] -= 1
            else:
                seen_titles.add(title)
        
        # Ensure all slides have titles
        for slide in slides:
            if not slide.get("title") or slide.get("title").lower() in ["untitled", "slide"]:
                slide_num = slide.get("slide_number", 1)
                bullet_points = slide.get("bullet_points", [])
                if bullet_points:
                    slide["title"] = self._generate_title_from_content(bullet_points[0])
                else:
                    slide["title"] = f"Slide {slide_num}"
        
        return slides
    
    def _generate_title_from_content(self, content: str) -> str:
        """Generate a title from content snippet"""
        # Take first sentence or first 8 words
        sentences = re.split(r'[.!?]+', content)
        if sentences:
            first_sentence = sentences[0].strip()
            words = first_sentence.split()[:8]
            title = ' '.join(words)
            # Clean up
            title = re.sub(r'[^\w\s]$', '', title)
            # Remove numeric prefixes
            title = re.sub(r'^\(\d+\)\s*', '', title)
            title = re.sub(r'^\d+\.\s*', '', title)
            return title[:60]
        return "Content"
    
    def _generate_unique_title_from_content(self, content: str, seen_titles: set) -> str:
        """Generate a unique title from content that hasn't been used"""
        base_title = self._generate_title_from_content(content)
        
        # If title is already used, try to make it unique
        if base_title in seen_titles:
            # Try extracting key topic words
            words = content.split()[:5]
            topic_words = [w for w in words if len(w) > 4 and w.lower() not in ['this', 'that', 'these', 'those', 'there']]
            if topic_words:
                base_title = ' '.join(topic_words[:3])
        
        # If still duplicate, add a suffix
        counter = 1
        unique_title = base_title
        while unique_title in seen_titles:
            unique_title = f"{base_title} {counter}"
            counter += 1
        
        return unique_title
    
    def _fallback_refinement(self, slides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback refinement when LLM is unavailable"""
        return self._ensure_consistency(slides)
    
    def _fallback_refine_single(self, slide: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback refinement for single slide"""
        # Basic cleanup
        title = slide.get("title", "Untitled")
        if not title or title.lower() in ["untitled", "slide"]:
            bullet_points = slide.get("bullet_points", [])
            if bullet_points:
                slide["title"] = self._generate_title_from_content(bullet_points[0])
            else:
                slide["title"] = f"Slide {slide.get('slide_number', 1)}"
        
        # Ensure bullets exist
        if not slide.get("bullet_points"):
            slide["bullet_points"] = ["Content pending"]
        
        return slide
