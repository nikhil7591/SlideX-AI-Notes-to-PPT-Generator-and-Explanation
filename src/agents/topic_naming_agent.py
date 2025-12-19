"""
Topic Naming Agent
Assigns meaningful, context-aware names to each topic/section
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
        # Newer LangChain versions
        from langchain_core.prompts import ChatPromptTemplate
        LLMChain = None  # Use direct invoke instead
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from ..config import Config


class TopicNamingAgent:
    """
    Agent responsible for assigning meaningful, context-aware names to topics.
    Ensures names are:
    - Descriptive and specific (not generic)
    - Contextually appropriate
    - Suitable for slide titles
    """
    
    def __init__(self):
        self.config = Config()
        self.llm = self._initialize_llm()
        self.use_langchain = LANGCHAIN_AVAILABLE
        self.use_genai = GENAI_AVAILABLE
    
    def _initialize_llm(self):
        """Initialize LLM for topic naming"""
        try:
            if LANGCHAIN_AVAILABLE:
                return ChatGoogleGenerativeAI(
                    model=self.config.GEMINI_MODEL,
                    temperature=0.5,  # Lower temperature for more consistent naming
                    google_api_key=self.config.GEMINI_API_KEY
                )
            elif GENAI_AVAILABLE:
                genai.configure(api_key=self.config.GEMINI_API_KEY)
                return genai.GenerativeModel(self.config.GEMINI_MODEL)
            else:
                return None
        except Exception as e:
            print(f"Error initializing Topic Naming Agent LLM: {e}")
            return None
    
    def name_topics(
        self, 
        text_content: str,
        topic_segments: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Assign meaningful names to topics based on content
        
        Args:
            text_content: The full text content
            topic_segments: List of topic segments with content
            context: Optional context metadata
            
        Returns:
            List of topics with assigned names
        """
        try:
            if not self.llm:
                return self._fallback_naming(topic_segments)
            
            if self.use_langchain:
                return self._langchain_name_topics(text_content, topic_segments, context)
            elif self.use_genai:
                return self._genai_name_topics(text_content, topic_segments, context)
            else:
                return self._fallback_naming(topic_segments)
        except Exception as e:
            print(f"Error in topic naming: {e}")
            return self._fallback_naming(topic_segments)
    
    def _langchain_name_topics(
        self, 
        text_content: str,
        topic_segments: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Name topics using LangChain"""
        try:
            # Prepare topic content summaries
            topic_summaries = []
            for i, segment in enumerate(topic_segments):
                content = segment.get('content', segment.get('text', ''))
                summary = content[:300] if content else ""
                topic_summaries.append(f"Topic {i+1}: {summary}")
            
            topics_text = "\n\n".join(topic_summaries)
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert at creating clear, descriptive, and context-aware topic names for presentations.
                
Your task is to assign meaningful names to each topic segment. The names should:
- Be specific and descriptive (avoid generic titles like "Introduction" or "Overview")
- Reflect the actual content of the topic
- Be suitable as slide titles (concise but informative)
- Be contextually aware of the overall document theme
- Use professional language appropriate for presentations"""),
                ("human", f"""Given the following text content and topic segments, assign a meaningful, context-aware name to each topic.

Full Document Context (first 1000 characters):
{text_content[:1000]}

Topic Segments:
{topics_text}

For each topic, provide:
1. A unique, descriptive name (2-8 words)
2. A brief rationale for the name choice

Format your response as JSON:
{{
    "topics": [
        {{
            "topic_index": 1,
            "name": "Descriptive Topic Name",
            "rationale": "Brief explanation"
        }},
        ...
    ]
}}

Topic Names:""")
            ])
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            result = chain.run({})
            
            # Parse JSON response
            try:
                parsed = json.loads(result)
                if isinstance(parsed, dict) and "topics" in parsed:
                    named_topics = []
                    for i, segment in enumerate(topic_segments):
                        # Find matching topic name
                        topic_name = None
                        for topic_info in parsed["topics"]:
                            if topic_info.get("topic_index") == i + 1:
                                topic_name = topic_info.get("name", segment.get('name', f"Topic {i+1}"))
                                break
                        
                        if not topic_name:
                            topic_name = self._extract_name_from_content(segment)
                        
                        named_topics.append({
                            **segment,
                            "name": topic_name,
                            "original_index": i
                        })
                    
                    return named_topics
            except json.JSONDecodeError:
                pass
            
            return self._parse_text_response(result, topic_segments)
            
        except Exception as e:
            print(f"LangChain topic naming error: {e}")
            return self._fallback_naming(topic_segments)
    
    def _genai_name_topics(
        self,
        text_content: str,
        topic_segments: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Name topics using direct GenAI"""
        try:
            topic_summaries = []
            for i, segment in enumerate(topic_segments):
                content = segment.get('content', segment.get('text', ''))
                summary = content[:300] if content else ""
                topic_summaries.append(f"Topic {i+1}: {summary}")
            
            topics_text = "\n\n".join(topic_summaries)
            
            prompt = f"""Given the following text content and topic segments, assign a meaningful, context-aware name to each topic.

Full Document Context (first 1000 characters):
{text_content[:1000]}

Topic Segments:
{topics_text}

For each topic, provide a unique, descriptive name (2-8 words). Names should:
- Be specific and descriptive (avoid generic titles)
- Reflect the actual content
- Be suitable as slide titles
- Be contextually aware

Format as a simple list, one name per line:
Topic 1: [Name]
Topic 2: [Name]
...

Topic Names:"""
            
            response = self.llm.generate_content(prompt)
            result = response.text.strip()
            
            return self._parse_text_response(result, topic_segments)
            
        except Exception as e:
            print(f"GenAI topic naming error: {e}")
            return self._fallback_naming(topic_segments)
    
    def _parse_text_response(self, response: str, topic_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse text response to extract topic names"""
        named_topics = []
        lines = response.split('\n')
        
        # Extract topic names from lines
        topic_names = {}
        for line in lines:
            # Match patterns like "Topic 1: Name" or "1. Name"
            match = re.match(r'(?:Topic\s+)?(\d+)[:.)]\s*(.+)', line, re.IGNORECASE)
            if match:
                idx = int(match.group(1)) - 1
                name = match.group(2).strip()
                if name:
                    topic_names[idx] = name
        
        # Assign names to segments
        for i, segment in enumerate(topic_segments):
            name = topic_names.get(i, self._extract_name_from_content(segment))
            named_topics.append({
                **segment,
                "name": name,
                "original_index": i
            })
        
        return named_topics
    
    def _extract_name_from_content(self, segment: Dict[str, Any]) -> str:
        """Extract a name from segment content as fallback"""
        content = segment.get('content', segment.get('text', ''))
        
        if not content:
            return segment.get('name', 'Untitled Topic')
        
        # Try to extract first sentence or key phrase
        sentences = re.split(r'[.!?]', content)
        if sentences:
            first_sentence = sentences[0].strip()
            # Use first 6-8 words as name
            words = first_sentence.split()[:8]
            name = ' '.join(words)
            # Remove trailing punctuation
            name = re.sub(r'[^\w\s]$', '', name)
            return name[:60]  # Limit length
        
        return segment.get('name', 'Untitled Topic')
    
    def _fallback_naming(self, topic_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback naming when LLM is unavailable"""
        named_topics = []
        
        for i, segment in enumerate(topic_segments):
            # Try to extract name from content
            name = self._extract_name_from_content(segment)
            
            named_topics.append({
                **segment,
                "name": name,
                "original_index": i
            })
        
        return named_topics
