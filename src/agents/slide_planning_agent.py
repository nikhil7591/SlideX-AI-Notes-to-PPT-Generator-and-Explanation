"""
Slide Planning Agent
Decides slide structure and distribution based on content and requirements
"""

from typing import List, Dict, Any, Optional
import json
import math

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


class SlidePlanningAgent:
    """
    Agent responsible for planning slide structure and content distribution.
    Ensures:
    - Exact number of slides as specified
    - Logical flow and structure
    - Balanced content distribution
    - No mixing of multiple main topics in a single slide
    """
    
    def __init__(self):
        self.config = Config()
        self.llm = self._initialize_llm()
        self.use_langchain = LANGCHAIN_AVAILABLE
        self.use_genai = GENAI_AVAILABLE
    
    def _initialize_llm(self):
        """Initialize LLM for slide planning"""
        try:
            if LANGCHAIN_AVAILABLE:
                return ChatGoogleGenerativeAI(
                    model=self.config.GEMINI_MODEL,
                    temperature=0.3,  # Low temperature for consistent planning
                    google_api_key=self.config.GEMINI_API_KEY
                )
            elif GENAI_AVAILABLE:
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                return genai.GenerativeModel(self.config.GEMINI_MODEL)
            else:
                return None
        except Exception as e:
            print(f"Error initializing Slide Planning Agent LLM: {e}")
            return None
    
    def plan_slides(
        self,
        named_topics: List[Dict[str, Any]],
        text_content: str,
        target_slide_count: int,
        template_style: str = "modern"
    ) -> List[Dict[str, Any]]:
        """
        Plan slide structure and distribution
        
        Args:
            named_topics: List of topics with assigned names
            text_content: Full text content for context
            target_slide_count: Exact number of slides to generate
            template_style: Template style (modern, academic)
            
        Returns:
            List of slide plans with structure and content distribution
        """
        try:
            if target_slide_count <= 0:
                return []
            
            if not self.llm:
                return self._fallback_planning(named_topics, target_slide_count)
            
            if self.use_langchain:
                return self._langchain_plan_slides(named_topics, text_content, target_slide_count, template_style)
            elif self.use_genai:
                return self._genai_plan_slides(named_topics, text_content, target_slide_count, template_style)
            else:
                return self._fallback_planning(named_topics, target_slide_count)
                
        except Exception as e:
            print(f"Error in slide planning: {e}")
            return self._fallback_planning(named_topics, target_slide_count)
    
    def _langchain_plan_slides(
        self,
        named_topics: List[Dict[str, Any]],
        text_content: str,
        target_slide_count: int,
        template_style: str
    ) -> List[Dict[str, Any]]:
        """Plan slides using LangChain"""
        try:
            # Prepare topic information
            topics_summary = []
            for i, topic in enumerate(named_topics):
                name = topic.get('name', f'Topic {i+1}')
                content = topic.get('content', topic.get('text', ''))[:200]
                topics_summary.append(f"{i+1}. {name}: {content}")
            
            topics_text = "\n".join(topics_summary)
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert presentation planner. Your task is to create a detailed slide plan that:
1. Generates EXACTLY the specified number of slides (no more, no less)
2. Ensures logical flow and progression
3. Distributes content evenly across slides
4. Never mixes multiple main topics in a single slide
5. Assigns unique, meaningful topic titles to each slide (NO numbering, NO repeated titles)
6. Determines appropriate bullet point distribution
7. Ensures each slide covers a DIFFERENT topic or section (NO repetition)
8. Divides input into distinct logical sections (Introduction, Problem Statement, Architecture, Components, Applications, Advantages, Challenges, Future Scope, Conclusion, etc.)

CRITICAL RULES:
- Each slide MUST have a UNIQUE topic title
- Each slide MUST cover a DIFFERENT section
- NO repeated titles across slides
- NO numeric headings like (1), (2), (3)
- NO auto-generated numbering
- One distinct section per slide only"""),
                ("human", f"""Create a slide plan for a presentation with EXACTLY {target_slide_count} slides.

Available Topics:
{topics_text}

Full Content Context (first 1500 characters):
{text_content[:1500]}

Template Style: {template_style}
- Modern: concise bullets, impactful titles, minimal text
- Academic: formal language, structured explanations, clear hierarchy

Create a plan with EXACTLY {target_slide_count} slides. 

CRITICAL RULES:
1. The LAST slide (slide {target_slide_count}) MUST be type "conclusion" with title "Conclusion"
2. All other slides must have UNIQUE, DISTINCT topics
3. NO two slides can have the same title
4. Each slide must cover a DIFFERENT section/topic from the content

For each slide, specify:
- Slide number (1 to {target_slide_count})
- Title (unique topic name like: Introduction, Problem Statement, Architecture, Components, Applications, Advantages, Challenges, Future Scope - NO numbering, NO repeated titles, NO "Conclusion" except for last slide)
- Content focus (which distinct topic/section - must be DIFFERENT from other slides)
- Estimated bullet points (3-5 for modern, 4-6 for academic)
- Slide type (title, content, conclusion - conclusion ONLY for slide {target_slide_count})

ANTI-REPETITION RULE: Before assigning a topic to a slide, ensure NO previous slide uses the same topic or title.

Format as JSON:
{{
    "slides": [
        {{
            "slide_number": 1,
            "title": "Slide Title",
            "content_focus": "Description of content",
            "bullet_count": 4,
            "slide_type": "title/content/conclusion",
            "topic_indices": [0]
        }},
        ...
    ]
}}

The plan must have EXACTLY {target_slide_count} slides.

Slide Plan:""")
            ])
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = chain.run({})
            
            # Parse JSON response
            try:
                parsed = json.loads(result)
                if isinstance(parsed, dict) and "slides" in parsed:
                    slides = parsed["slides"]
                    # Ensure exact count
                    slides = slides[:target_slide_count]
                    
                    # Ensure last slide is conclusion
                    if slides and target_slide_count > 1:
                        last_slide = slides[-1]
                        last_slide["slide_number"] = target_slide_count
                        last_slide["slide_type"] = "conclusion"
                        if "conclusion" not in last_slide.get("title", "").lower():
                            last_slide["title"] = "Conclusion"
                    
                    while len(slides) < target_slide_count:
                        # Add filler slides if needed (but not conclusion)
                        slide_num = len(slides) + 1
                        if slide_num == target_slide_count:
                            # Last slide should be conclusion
                            slides.append({
                                "slide_number": slide_num,
                                "title": "Conclusion",
                                "content_focus": "Summary and conclusion",
                                "bullet_count": 4,
                                "slide_type": "conclusion",
                                "topic_indices": []
                            })
                        else:
                            slides.append({
                                "slide_number": slide_num,
                                "title": f"Topic {slide_num}",
                                "content_focus": "Additional information",
                                "bullet_count": 4,
                                "slide_type": "content",
                                "topic_indices": []
                            })
                    
                    # Ensure last slide is conclusion
                    if slides and target_slide_count > 1:
                        slides[-1]["slide_number"] = target_slide_count
                        slides[-1]["slide_type"] = "conclusion"
                        slides[-1]["title"] = "Conclusion"
                    
                    return slides[:target_slide_count]
            except json.JSONDecodeError:
                pass
            
            return self._fallback_planning(named_topics, target_slide_count)
            
        except Exception as e:
            print(f"LangChain slide planning error: {e}")
            return self._fallback_planning(named_topics, target_slide_count)
    
    def _genai_plan_slides(
        self,
        named_topics: List[Dict[str, Any]],
        text_content: str,
        target_slide_count: int,
        template_style: str
    ) -> List[Dict[str, Any]]:
        """Plan slides using direct GenAI"""
        try:
            topics_summary = []
            for i, topic in enumerate(named_topics):
                name = topic.get('name', f'Topic {i+1}')
                content = topic.get('content', topic.get('text', ''))[:200]
                topics_summary.append(f"{i+1}. {name}: {content}")
            
            topics_text = "\n".join(topics_summary)
            
            prompt = f"""Create a slide plan for EXACTLY {target_slide_count} slides.

Available Topics:
{topics_text}

Template Style: {template_style}

For each slide (1 to {target_slide_count}), provide:
Slide [N]: [Title] | [Content Focus] | [Bullet Count] | [Type]

Slide Plan:"""
            
            response = self.llm.generate_content(prompt)
            result = response.text.strip()
            
            return self._parse_text_plan(result, target_slide_count, named_topics)
            
        except Exception as e:
            print(f"GenAI slide planning error: {e}")
            return self._fallback_planning(named_topics, target_slide_count)
    
    def _parse_text_plan(
        self,
        response: str,
        target_slide_count: int,
        named_topics: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse text response to extract slide plan"""
        import re
        
        slides = []
        lines = response.split('\n')
        
        for line in lines:
            # Match pattern: "Slide N: Title | Focus | Count | Type"
            match = re.match(r'Slide\s+(\d+):\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\w+)', line, re.IGNORECASE)
            if match:
                slide_num = int(match.group(1))
                title = match.group(2).strip()
                focus = match.group(3).strip()
                bullet_count = int(match.group(4))
                slide_type = match.group(5).strip().lower()
                
                slides.append({
                    "slide_number": slide_num,
                    "title": title,
                    "content_focus": focus,
                    "bullet_count": bullet_count,
                    "slide_type": slide_type,
                    "topic_indices": []
                })
        
        # Ensure exact count
        if len(slides) < target_slide_count:
            return self._fallback_planning(named_topics, target_slide_count)
        
        return slides[:target_slide_count]
    
    def _fallback_planning(
        self,
        named_topics: List[Dict[str, Any]],
        target_slide_count: int
    ) -> List[Dict[str, Any]]:
        """Fallback planning when LLM is unavailable"""
        if not named_topics or target_slide_count <= 0:
            return []
        
        slides = []
        num_topics = len(named_topics)
        
        # Calculate distribution
        slides_per_topic = max(1, target_slide_count // num_topics) if num_topics > 0 else 1
        remaining_slides = target_slide_count
        
        # Add title slide
        if remaining_slides > 0:
            slides.append({
                "slide_number": 1,
                "title": named_topics[0].get('name', 'Presentation Overview') if named_topics else "Presentation",
                "content_focus": "Introduction and overview",
                "bullet_count": 4,
                "slide_type": "title",
                "topic_indices": []
            })
            remaining_slides -= 1
        
        # Distribute topics across slides
        topic_idx = 0
        slide_num = 2
        
        while remaining_slides > 0 and topic_idx < num_topics:
            topic = named_topics[topic_idx]
            
            # Determine how many slides for this topic
            topic_slides = min(slides_per_topic, remaining_slides)
            
            for i in range(topic_slides):
                if remaining_slides > 0:
                    slides.append({
                        "slide_number": slide_num,
                        "title": topic.get('name', f'Topic {topic_idx + 1}'),
                        "content_focus": f"Content from topic: {topic.get('name', 'Unknown')}",
                        "bullet_count": 4,
                        "slide_type": "content",
                        "topic_indices": [topic_idx]
                    })
                    slide_num += 1
                    remaining_slides -= 1
            
            topic_idx += 1
        
        # Always ensure conclusion is the last slide
        # Remove any existing conclusion slides first
        slides = [s for s in slides if s.get("slide_type", "").lower() != "conclusion"]
        
        # Calculate how many content slides we have
        content_slides = slides[:target_slide_count - 1] if target_slide_count > 1 else slides[:target_slide_count]
        
        # Fill remaining slots with additional content slides if needed
        while len(content_slides) < target_slide_count - 1:
            content_slides.append({
                "slide_number": len(content_slides) + 1,
                "title": f"Topic {len(content_slides) + 1}",
                "content_focus": "Additional information",
                "bullet_count": 4,
                "slide_type": "content",
                "topic_indices": []
            })
        
        # Always add conclusion as the last slide (if we have more than 1 slide)
        if target_slide_count > 1:
            conclusion_slide = {
                "slide_number": target_slide_count,
                "title": "Conclusion",
                "content_focus": "Summary and key takeaways",
                "bullet_count": 4,
                "slide_type": "conclusion",
                "topic_indices": []
            }
            return content_slides[:target_slide_count - 1] + [conclusion_slide]
        else:
            return content_slides[:target_slide_count]
