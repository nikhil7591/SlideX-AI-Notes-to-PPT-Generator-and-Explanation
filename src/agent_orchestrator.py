"""
Agent Orchestrator
Coordinates the multi-agent workflow for SlideX
"""

from typing import List, Dict, Any, Optional
import re

from .agents import (
    DocumentUnderstandingAgent,
    TopicNamingAgent,
    SlidePlanningAgent,
    ContentGenerationAgent,
    RefinementAgent
)
from .config import Config


class SlideXOrchestrator:
    """
    Orchestrates the multi-agent workflow:
    1. Document Understanding Agent
    2. Topic Naming Agent
    3. Slide Planning Agent
    4. Content Generation Agent
    5. Refinement Agent
    """
    
    def __init__(self):
        self.config = Config()
        
        # Initialize all agents
        self.doc_understanding_agent = DocumentUnderstandingAgent()
        self.topic_naming_agent = TopicNamingAgent()
        self.slide_planning_agent = SlidePlanningAgent()
        self.content_generation_agent = ContentGenerationAgent()
        self.refinement_agent = RefinementAgent()
    
    def generate_presentation(
        self,
        input_content: str,
        input_type: str = "text",
        file_path: Optional[str] = None,
        target_slide_count: int = 20,
        template_style: str = "modern",
        explanation_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate presentation using the multi-agent workflow
        
        Args:
            input_content: Input content (text, file path, etc.)
            input_type: Type of input ("text", "image", "voice", "document")
            file_path: Optional file path
            target_slide_count: Exact number of slides to generate
            template_style: Template style ("modern", "academic")
            explanation_level: Explanation level ("standard", "detailed")
            
        Returns:
            Dictionary with generated slides and metadata
        """
        try:
            # Step 1: Document Understanding Agent
            print("Step 1: Document Understanding Agent - Processing input...")
            understanding_result = self.doc_understanding_agent.process_input(
                input_content,
                input_type,
                file_path
            )
            
            if not understanding_result.get("success"):
                return {
                    "success": False,
                    "error": understanding_result.get("error", "Document understanding failed"),
                    "slides": []
                }
            
            cleaned_text = understanding_result.get("cleaned_text", "")
            if not cleaned_text:
                return {
                    "success": False,
                    "error": "No content extracted from input",
                    "slides": []
                }
            
            # Extract insights
            insights = self.doc_understanding_agent.extract_key_insights(cleaned_text)
            print(f"Extracted {insights.get('word_count', 0)} words, {insights.get('paragraph_count', 0)} paragraphs")
            
            # Step 2: Segment content into topics
            print("Step 2: Segmenting content into topics...")
            topic_segments = self._segment_content(cleaned_text, insights)
            print(f"Segmented into {len(topic_segments)} topics")
            
            # Step 3: Topic Naming Agent
            print("Step 3: Topic Naming Agent - Assigning meaningful names...")
            named_topics = self.topic_naming_agent.name_topics(
                cleaned_text,
                topic_segments,
                insights
            )
            print(f"Named {len(named_topics)} topics")
            
            # Step 4: Slide Planning Agent
            print(f"Step 4: Slide Planning Agent - Planning {target_slide_count} slides...")
            slide_plans = self.slide_planning_agent.plan_slides(
                named_topics,
                cleaned_text,
                target_slide_count,
                template_style
            )
            print(f"Created plan for {len(slide_plans)} slides")
            
            # Step 5: Content Generation Agent
            print("Step 5: Content Generation Agent - Generating slide content...")
            generated_slides = []
            for i, plan in enumerate(slide_plans):
                # Pass previously generated slides to avoid repetition
                previous_slides = generated_slides[:i] if i > 0 else None
                slide_content = self.content_generation_agent.generate_slide_content(
                    plan,
                    cleaned_text,
                    template_style,
                    explanation_level,
                    previous_slides=previous_slides
                )
                generated_slides.append(slide_content)
            
            print(f"Generated content for {len(generated_slides)} slides")
            
            # Step 6: Refinement Agent
            print("Step 6: Refinement Agent - Refining slides...")
            refined_slides = self.refinement_agent.refine_slides(
                generated_slides,
                template_style,
                explanation_level
            )
            print(f"Refined {len(refined_slides)} slides")
            
            # Ensure exact slide count and add conclusion slide
            refined_slides = refined_slides[:target_slide_count]
            
            # Remove any existing conclusion slides first
            refined_slides = [s for s in refined_slides if s.get("slide_type", "").lower() != "conclusion"]
            
            # Ensure we have enough slides for content + conclusion
            content_slides_count = max(1, target_slide_count - 1)
            content_slides = refined_slides[:content_slides_count]
            
            # Always add conclusion as the last slide
            if target_slide_count > 1:
                conclusion_slide = self._create_conclusion_slide(
                    content_slides,
                    cleaned_text,
                    target_slide_count
                )
                refined_slides = content_slides + [conclusion_slide]
            else:
                refined_slides = content_slides
            
            # Final check: ensure exact count
            refined_slides = refined_slides[:target_slide_count]
            
            return {
                "success": True,
                "slides": refined_slides[:target_slide_count],
                "slide_count": len(refined_slides[:target_slide_count]),
                "original_text_length": len(cleaned_text),
                "cleaned_text": cleaned_text,  # Include cleaned text for explanations
                "template_style": template_style,
                "explanation_level": explanation_level,
                "processing_steps": {
                    "document_understanding": "completed",
                    "topic_naming": "completed",
                    "slide_planning": "completed",
                    "content_generation": "completed",
                    "refinement": "completed"
                }
            }
            
        except Exception as e:
            print(f"Error in orchestration: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "slides": []
            }
    
    def _segment_content(self, text: str, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Segment content into topic segments
        
        Args:
            text: Full text content
            insights: Insights from document understanding
            
        Returns:
            List of topic segments
        """
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # Fallback: split by sentences
            sentences = re.split(r'[.!?]+', text)
            paragraphs = [s.strip() for s in sentences if s.strip()]
        
        # Estimate topics
        estimated_topics = insights.get("estimated_topics", max(3, len(paragraphs) // 3))
        
        # Group paragraphs into topics
        paragraphs_per_topic = max(1, len(paragraphs) // estimated_topics) if estimated_topics > 0 else 1
        
        topic_segments = []
        current_segment = []
        segment_idx = 0
        
        for i, paragraph in enumerate(paragraphs):
            current_segment.append(paragraph)
            
            # Check if we should start a new segment
            if len(current_segment) >= paragraphs_per_topic or i == len(paragraphs) - 1:
                if current_segment:
                    topic_segments.append({
                        "topic_index": segment_idx,
                        "content": "\n\n".join(current_segment),
                        "text": "\n\n".join(current_segment),
                        "paragraph_count": len(current_segment)
                    })
                    segment_idx += 1
                    current_segment = []
        
        # Ensure we have at least one segment
        if not topic_segments:
            topic_segments.append({
                "topic_index": 0,
                "content": text[:1000],
                "text": text[:1000],
                "paragraph_count": 1
            })
        
        return topic_segments
    
    def _create_conclusion_slide(
        self,
        content_slides: List[Dict[str, Any]],
        original_text: str,
        slide_number: int
    ) -> Dict[str, Any]:
        """Create a conclusion slide summarizing the presentation"""
        # Extract key points from content slides
        key_topics = []
        for slide in content_slides[:5]:  # Get topics from first 5 slides
            title = slide.get("title", "")
            if title and title.lower() not in ["conclusion", "summary", "introduction", "overview"]:
                # Clean title (remove numbering if any)
                title = re.sub(r'^\d+[.\s)]*\s*', '', title)
                title = re.sub(r'^\(\d+\)\s*', '', title)
                if title.strip():
                    key_topics.append(title.strip())
        
        # Create conclusion bullet points
        bullet_points = [
            "Summary of key concepts and main topics discussed",
            "Important insights and findings from the presentation",
            "Key takeaways for the audience"
        ]
        
        if key_topics:
            # Add specific topics covered
            topics_text = ", ".join(key_topics[:3])
            bullet_points.insert(0, f"Covered topics include: {topics_text}")
        
        return {
            "slide_number": slide_number,
            "title": "Conclusion",
            "bullet_points": bullet_points[:5],
            "slide_type": "conclusion",
            "content_focus": "Summary and conclusion of the presentation"
        }
