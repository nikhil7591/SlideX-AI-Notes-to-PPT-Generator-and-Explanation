"""
Content Generation Agent - FIXED VERSION
Generates UNIQUE content for each slide with NO repetition
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
    try:
        from langchain.prompts import ChatPromptTemplate
        from langchain.chains import LLMChain
    except ImportError:
        from langchain_core.prompts import ChatPromptTemplate
        LLMChain = None
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from ..config import Config


class ContentGenerationAgent:
    """
    FIXED: Agent generates UNIQUE content for each slide
    """
    
    def __init__(self):
        self.config = Config()
        self.llm = self._initialize_llm()
        self.use_langchain = LANGCHAIN_AVAILABLE
        self.use_genai = GENAI_AVAILABLE
        # Track used content to prevent repetition
        self.used_titles = set()
        self.used_content = set()
    
    def _initialize_llm(self):
        """Initialize LLM for content generation"""
        try:
            if not self.config.GEMINI_API_KEY:
                print("ERROR: GEMINI_API_KEY is not set!")
                return None
            
            if LANGCHAIN_AVAILABLE:
                print(f"Initializing LangChain Gemini with model: {self.config.GEMINI_MODEL}")
                llm = ChatGoogleGenerativeAI(
                    model=self.config.GEMINI_MODEL,
                    temperature=0.7,
                    google_api_key=self.config.GEMINI_API_KEY
                )
                print("✓ LangChain Gemini initialized")
                return llm
            elif GENAI_AVAILABLE:
                print(f"Initializing Direct GenAI with model: {self.config.GEMINI_MODEL}")
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                model = genai.GenerativeModel(self.config.GEMINI_MODEL)
                print("✓ Direct GenAI initialized")
                return model
            else:
                print("ERROR: No AI library available!")
                return None
        except Exception as e:
            print(f"ERROR initializing LLM: {e}")
            return None
    
    def generate_slide_content(
        self,
        slide_plan: Dict[str, Any],
        text_content: str,
        template_style: str = "modern",
        explanation_level: str = "standard",
        previous_slides: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate UNIQUE content for a single slide
        """
        try:
            if not self.llm:
                print("WARNING: LLM not initialized, using fallback")
                return self._fallback_content_generation(slide_plan, text_content)
            
            slide_num = slide_plan.get('slide_number', 1)
            print(f"\n{'='*60}")
            print(f"Generating UNIQUE content for slide {slide_num}")
            print(f"{'='*60}")
            
            if self.use_langchain:
                result = self._langchain_generate_content(
                    slide_plan, text_content, template_style, 
                    explanation_level, previous_slides
                )
            elif self.use_genai:
                result = self._genai_generate_content(
                    slide_plan, text_content, template_style,
                    explanation_level, previous_slides
                )
            else:
                return self._fallback_content_generation(slide_plan, text_content)
            
            # Track used content
            title = result.get('title', '')
            if title:
                self.used_titles.add(title.lower())
            for bullet in result.get('bullet_points', []):
                self.used_content.add(bullet.lower()[:50])
            
            print(f"✓ Generated: '{title}' with {len(result.get('bullet_points', []))} bullets")
            return result
                
        except Exception as e:
            print(f"ERROR generating slide content: {e}")
            return self._fallback_content_generation(slide_plan, text_content)
    
    def _extract_unique_content_section(
        self,
        text_content: str,
        slide_number: int,
        focus_keywords: str,
        previous_slides: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Extract a UNIQUE section of content that hasn't been used before
        """
        # Split content into paragraphs
        paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # Fallback: split by sentences
            sentences = re.split(r'[.!?]+', text_content)
            paragraphs = [s.strip() for s in sentences if len(s.strip()) > 50]
        
        # Build exclusion set from previous slides
        used_content_phrases = set()
        if previous_slides:
            for prev_slide in previous_slides:
                # Add titles
                prev_title = prev_slide.get('title', '')
                if prev_title:
                    used_content_phrases.add(prev_title.lower())
                
                # Add bullet points
                for bullet in prev_slide.get('bullet_points', []):
                    # Store first 30 chars as phrase identifier
                    phrase = bullet.lower()[:30]
                    used_content_phrases.add(phrase)
                    # Also add individual words
                    words = bullet.lower().split()
                    for word in words:
                        if len(word) > 5:
                            used_content_phrases.add(word)
        
        # Score paragraphs by relevance and uniqueness
        keyword_list = focus_keywords.lower().split()
        scored_paragraphs = []
        
        for para_idx, paragraph in enumerate(paragraphs):
            para_lower = paragraph.lower()
            
            # Check if this paragraph was already used
            is_used = False
            para_words = set(para_lower.split())
            for used_phrase in used_content_phrases:
                if used_phrase in para_lower:
                    is_used = True
                    break
                # Check word overlap
                if len(para_words & {used_phrase}) > 0:
                    is_used = True
                    break
            
            if is_used:
                continue  # Skip used paragraphs
            
            # Score by keyword relevance
            keyword_score = sum(1 for kw in keyword_list if kw in para_lower and len(kw) > 3)
            
            # Add position score to ensure different sections
            position_score = abs(para_idx - (slide_number * 3)) / len(paragraphs)
            
            total_score = keyword_score + (1.0 - position_score)
            
            if keyword_score > 0 or para_idx % 3 == (slide_number % 3):
                scored_paragraphs.append((total_score, paragraph))
        
        # Sort by score
        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
        
        # Take top unique paragraphs
        unique_paragraphs = [para for score, para in scored_paragraphs[:5]]
        
        if not unique_paragraphs:
            # Fallback: use position-based selection
            start_idx = (slide_number * 2) % len(paragraphs)
            end_idx = min(start_idx + 3, len(paragraphs))
            unique_paragraphs = paragraphs[start_idx:end_idx]
        
        result = '\n\n'.join(unique_paragraphs)
        return result[:2000]
    
    def _langchain_generate_content(
        self,
        slide_plan: Dict[str, Any],
        text_content: str,
        template_style: str,
        explanation_level: str,
        previous_slides: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate content using LangChain with STRONG anti-repetition"""
        try:
            slide_num = slide_plan.get("slide_number", 1)
            planned_title = slide_plan.get("title", "Untitled")
            content_focus = slide_plan.get("content_focus", "")
            bullet_count = slide_plan.get("bullet_count", 4)
            slide_type = slide_plan.get("slide_type", "content")
            
            # Extract UNIQUE content section
            relevant_content = self._extract_unique_content_section(
                text_content,
                slide_num,
                content_focus,
                previous_slides
            )
            
            # Build STRONG exclusion context
            exclusion_context = ""
            if previous_slides:
                prev_titles = []
                prev_bullets = []
                
                for prev_slide in previous_slides:
                    title = prev_slide.get("title", "")
                    if title:
                        # Clean title
                        clean_title = re.sub(r'^\d+[.\s)]*\s*', '', title)
                        clean_title = re.sub(r'^\(\d+\)\s*', '', clean_title)
                        prev_titles.append(clean_title.strip())
                    
                    bullets = prev_slide.get("bullet_points", [])
                    prev_bullets.extend(bullets)
                
                if prev_titles or prev_bullets:
                    exclusion_context = f"""

⚠️ CRITICAL ANTI-REPETITION RULES ⚠️

FORBIDDEN TITLES (DO NOT USE):
{', '.join(prev_titles[-10:])}

FORBIDDEN CONTENT (DO NOT REPEAT):
{' | '.join(prev_bullets[-15:])}

YOU MUST:
1. Create a COMPLETELY DIFFERENT title from the forbidden list
2. Use COMPLETELY DIFFERENT content from previous slides
3. Focus ONLY on NEW information from the provided content
4. If the content section doesn't have enough unique information, extract sub-topics or specific details
"""
            
            # Style instructions
            style_instructions = {
                "modern": "Concise, impactful bullets (5-10 words each). Clear hierarchy.",
                "academic": "Formal, structured explanations (10-15 words per bullet). Include context."
            }
            style_guide = style_instructions.get(template_style, style_instructions["modern"])
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", f"""You are an expert presentation content creator with a STRICT NO-REPETITION policy.

YOUR MISSION:
- Generate UNIQUE content for each slide
- NEVER repeat titles from previous slides
- NEVER repeat bullet points from previous slides
- Extract DIFFERENT information from the provided content
- Focus on specific details, sub-topics, or aspects

QUALITY RULES:
1. Titles must be specific and descriptive (NOT generic)
2. Each bullet must convey distinct information
3. Use the {template_style} style: {style_guide}
4. Ground ALL content in the provided text (no hallucination)
"""),
                ("human", f"""Generate UNIQUE content for slide #{slide_num}:

Planned Title: {planned_title}
Content Focus: {content_focus}
Slide Type: {slide_type}
Required Bullets: {bullet_count}
Template: {template_style}

UNIQUE Content Section (ONLY use this):
{relevant_content}{exclusion_context}

INSTRUCTIONS:
1. Create a UNIQUE title that's DIFFERENT from all previous titles
2. Generate {bullet_count} UNIQUE bullet points with NEW information
3. Each bullet must be DIFFERENT from previous slides
4. Focus on specific details or aspects from the content section

Format:
TITLE:
[Unique descriptive title - NO numbering, NO generic words]

BULLET_POINTS:
• [Specific detail 1]
• [Specific detail 2]
• [Specific detail 3]
...

Generate UNIQUE content now:""")
            ])
            
            print(f"Calling LangChain Gemini API for slide {slide_num}...")
            
            try:
                messages = prompt_template.format_messages()
                result = self.llm.invoke(messages)
                
                if hasattr(result, 'content'):
                    result_text = result.content
                elif hasattr(result, 'text'):
                    result_text = result.text
                else:
                    result_text = str(result)
            except Exception as chain_error:
                if LLMChain is not None:
                    chain = LLMChain(llm=self.llm, prompt=prompt_template)
                    result_text = chain.run({})
                else:
                    raise chain_error
            
            if not result_text or len(str(result_text).strip()) < 10:
                print("WARNING: Response too short")
                return self._fallback_content_generation(slide_plan, text_content)
            
            print(f"✓ Received response from LangChain ({len(str(result_text))} chars)")
            
            parsed_result = self._parse_content_response(str(result_text), slide_plan)
            
            # Validate uniqueness
            if not self._validate_uniqueness(parsed_result, previous_slides):
                print("⚠️ WARNING: Generated content might have duplicates, regenerating...")
                # Try one more time with even stronger prompt
                return self._fallback_content_generation(slide_plan, text_content)
            
            print(f"✓ Validated UNIQUE content for slide {slide_num}")
            return parsed_result
            
        except Exception as e:
            print(f"LangChain content generation error: {e}")
            return self._fallback_content_generation(slide_plan, text_content)
    
    def _genai_generate_content(
        self,
        slide_plan: Dict[str, Any],
        text_content: str,
        template_style: str,
        explanation_level: str,
        previous_slides: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate content using GenAI with anti-repetition"""
        try:
            slide_num = slide_plan.get("slide_number", 1)
            planned_title = slide_plan.get("title", "Untitled")
            content_focus = slide_plan.get("content_focus", "")
            bullet_count = slide_plan.get("bullet_count", 4)
            
            # Extract unique content
            relevant_content = self._extract_unique_content_section(
                text_content,
                slide_num,
                content_focus,
                previous_slides
            )
            
            # Build exclusion list
            exclusion_info = ""
            if previous_slides:
                prev_titles = [s.get('title', '') for s in previous_slides]
                prev_bullets = []
                for s in previous_slides:
                    prev_bullets.extend(s.get('bullet_points', []))
                
                exclusion_info = f"""
FORBIDDEN TITLES: {', '.join(prev_titles[-8:])}
FORBIDDEN CONTENT: {' | '.join(prev_bullets[-12:])}
"""
            
            prompt = f"""Create UNIQUE content for slide {slide_num}:

Title: {planned_title}
Focus: {content_focus}
Bullets: {bullet_count}
Style: {template_style}

Unique Content (ONLY use this):
{relevant_content}
{exclusion_info}

RULES:
- Title must be UNIQUE (different from forbidden titles)
- Bullets must be UNIQUE (different from forbidden content)
- Extract NEW information only

Format:
TITLE:
[Unique title]

BULLET_POINTS:
• [Unique bullet 1]
• [Unique bullet 2]
...

Generate:"""
            
            print(f"Calling Gemini API for slide {slide_num}...")
            response = self.llm.generate_content(prompt)
            
            if not response or not hasattr(response, 'text'):
                print("ERROR: Invalid response from Gemini")
                return self._fallback_content_generation(slide_plan, text_content)
            
            result = response.text.strip()
            print(f"✓ Received response ({len(result)} chars)")
            
            parsed_result = self._parse_content_response(result, slide_plan)
            
            if not self._validate_uniqueness(parsed_result, previous_slides):
                print("⚠️ WARNING: Possible duplicates detected")
            
            return parsed_result
            
        except Exception as e:
            print(f"ERROR in GenAI content generation: {e}")
            return self._fallback_content_generation(slide_plan, text_content)
    
    def _validate_uniqueness(
        self,
        generated_slide: Dict[str, Any],
        previous_slides: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Validate that generated content is unique"""
        if not previous_slides:
            return True
        
        title = generated_slide.get('title', '').lower()
        bullets = [b.lower() for b in generated_slide.get('bullet_points', [])]
        
        # Check title uniqueness
        for prev_slide in previous_slides:
            prev_title = prev_slide.get('title', '').lower()
            if title == prev_title:
                print(f"⚠️ Duplicate title detected: '{title}'")
                return False
        
        # Check bullet uniqueness (fuzzy match)
        for bullet in bullets:
            bullet_words = set(bullet.split())
            for prev_slide in previous_slides:
                for prev_bullet in prev_slide.get('bullet_points', []):
                    prev_words = set(prev_bullet.lower().split())
                    # Check word overlap
                    overlap = len(bullet_words & prev_words)
                    if overlap > len(bullet_words) * 0.7:  # 70% overlap
                        print(f"⚠️ Similar bullet detected: '{bullet[:50]}...'")
                        return False
        
        return True
    
    def _parse_content_response(
        self,
        response: str,
        slide_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse LLM response"""
        title = slide_plan.get("title", "Untitled Slide")
        bullet_points = []
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TITLE:'):
                current_section = 'title'
            elif line.startswith('BULLET_POINTS:'):
                current_section = 'bullets'
            elif line and current_section == 'title':
                title_text = line.replace('TITLE:', '').strip()
                if title_text and title_text != title:
                    title = title_text
                current_section = None
            elif line and current_section == 'bullets':
                bullet_text = line.strip()
                bullet_text = re.sub(r'^[•\-\*\d+\.]\s*', '', bullet_text)
                if bullet_text:
                    bullet_points.append(bullet_text)
        
        # Fallback extraction
        if not bullet_points:
            for line in lines:
                line = line.strip()
                if re.match(r'^[•\-\*\d+\.]\s+', line):
                    bullet_text = re.sub(r'^[•\-\*\d+\.]\s+', '', line).strip()
                    if bullet_text:
                        bullet_points.append(bullet_text)
        
        # Ensure content exists
        if not bullet_points:
            content_focus = slide_plan.get("content_focus", "")
            bullet_points = [content_focus] if content_focus else ["Content pending"]
        
        # Clean title
        title = re.sub(r'^\(\d+\)\s*', '', title)
        title = re.sub(r'^\d+\.\s*', '', title)
        title = re.sub(r'^Slide\s+\d+:\s*', '', title, flags=re.IGNORECASE)
        
        return {
            "slide_number": slide_plan.get("slide_number", 1),
            "title": title.strip(),
            "bullet_points": bullet_points[:8],
            "slide_type": slide_plan.get("slide_type", "content"),
            "content_focus": slide_plan.get("content_focus", "")
        }
    
    def _fallback_content_generation(
        self,
        slide_plan: Dict[str, Any],
        text_content: str
    ) -> Dict[str, Any]:
        """Fallback: Extract unique content section"""
        title = slide_plan.get("title", "Untitled Slide")
        title = re.sub(r'^\(\d+\)\s*', '', title)
        title = re.sub(r'^\d+\.\s*', '', title)
        title = title.strip()
        
        slide_num = slide_plan.get("slide_number", 1)
        
        # Extract unique section based on slide number
        sentences = re.split(r'[.!?]+', text_content)
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Use different sections for each slide
        start_idx = ((slide_num - 1) * 3) % len(valid_sentences)
        end_idx = min(start_idx + 5, len(valid_sentences))
        
        relevant_sentences = valid_sentences[start_idx:end_idx]
        bullet_points = [sent[:100] for sent in relevant_sentences if sent]
        
        if not bullet_points:
            bullet_points = [f"Content for topic: {title}"]
        
        return {
            "slide_number": slide_num,
            "title": title,
            "bullet_points": bullet_points[:5],
            "slide_type": slide_plan.get("slide_type", "content"),
            "content_focus": slide_plan.get("content_focus", "")
        }