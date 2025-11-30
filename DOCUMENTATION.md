# SlideX Documentation 📚

Comprehensive technical documentation for the SlideX AI Presentation Generator.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Modules](#core-modules)
3. [API Reference](#api-reference)
4. [Configuration](#configuration)
5. [Development Guide](#development-guide)
6. [Deployment](#deployment)
7. [Testing](#testing)
8. [Performance Optimization](#performance-optimization)

---

## Architecture Overview

### System Design

SlideX follows a modular architecture pattern with clear separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Business Logic │    │   Data Layer    │
│                 │    │                  │    │                 │
│ Streamlit UI    │◄──►│   AI Agents      │◄──►│  Document Store │
│ User Interface  │    │ Content Gen      │    │ File System     │
│ File Upload     │    │ PPT Generation   │    │ Temp Files      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Flow

1. **Document Upload** → File validation → Temporary storage
2. **Document Processing** → Text extraction → Content analysis
3. **AI Content Generation** → Structured content → Slide planning
4. **PowerPoint Generation** → Template application → File creation
5. **Explanation Generation** → Additional insights → Enhanced content

### Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **AI/ML**: Google Gemini AI, LangChain
- **Document Processing**: PyPDF2, python-docx
- **PowerPoint Generation**: python-pptx
- **NLP**: NLTK, spaCy

---

## Core Modules

### 1. Document Processor (`src/document_processor.py`)

#### Purpose
Handles document parsing and text extraction from multiple file formats.

#### Key Classes

```python
class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from supported document formats"""
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        
    def analyze_structure(self, text: str) -> dict:
        """Analyze document structure and identify sections"""
```

#### Methods

- `extract_text()`: Main text extraction method
- `clean_text()`: Text preprocessing and cleaning
- `analyze_structure()`: Document structure analysis
- `validate_file()`: File format validation

#### Supported Formats

| Format | Library | Features |
|--------|---------|----------|
| PDF | PyPDF2, pypdf | Text extraction, metadata |
| DOCX | python-docx | Full document parsing |
| TXT | Native | Basic text handling |

### 2. AI Agent (`src/ai_agent.py`)

#### Purpose
Manages AI-powered content generation using Google Gemini AI.

#### Key Classes

```python
class AIAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = self._initialize_model()
    
    def generate_content(self, text: str, style: str) -> dict:
        """Generate structured presentation content"""
        
    def structure_slides(self, content: str) -> list:
        """Structure content into slides"""
```

#### AI Models

- **Primary**: Google Gemini Pro
- **Fallback**: Direct Gemini API
- **Framework**: LangChain integration

#### Content Generation Process

1. **Input Analysis**: Topic identification, content summarization
2. **Structure Planning**: Slide sequence, key points determination
3. **Content Generation**: Professional content creation
4. **Quality Assurance**: Content validation and enhancement

### 3. PowerPoint Generator (`src/ppt_generator.py`)

#### Purpose
Creates professional PowerPoint presentations from AI-generated content.

#### Key Classes

```python
class PPTGenerator:
    def __init__(self):
        self.templates = {
            'academic': AcademicTemplate(),
            'modern': ModernTemplate(),
            'professional': ProfessionalTemplate()
        }
    
    def create_presentation(self, content: dict, style: str) -> bytes:
        """Generate PowerPoint file"""
        
    def apply_template(self, prs, style: str):
        """Apply visual template to presentation"""
```

#### Template System

Each template includes:
- **Color Scheme**: Primary and secondary colors
- **Typography**: Font families and sizes
- **Layout**: Slide master layouts
- **Elements**: Logos, placeholders, backgrounds

#### Slide Types

- **Title Slide**: Main presentation title
- **Content Slide**: Key points and explanations
- **Summary Slide**: Conclusions and takeaways
- **Thank You Slide**: Closing slide

### 4. Explanation Agent (`src/explanation_agent.py`)

#### Purpose
Generates intelligent explanations and additional content for slides.

#### Key Classes

```python
class ExplanationAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = self._initialize_model()
    
    def generate_explanations(self, slide_content: dict) -> dict:
        """Generate comprehensive explanations"""
        
    def create_examples(self, topic: str) -> list:
        """Generate real-world examples"""
```

#### Explanation Types

1. **Slide Explanations**: Detailed breakdowns
2. **Real-World Examples**: Practical applications
3. **Key Terminology**: Important definitions
4. **Discussion Questions**: Interactive elements
5. **Learning Resources**: Additional materials
6. **Presentation Summary**: Comprehensive overview

---

## API Reference

### DocumentProcessor API

```python
# Initialize processor
processor = DocumentProcessor()

# Extract text
text = processor.extract_text("document.pdf")

# Clean text
clean_text = processor.clean_text(text)

# Analyze structure
structure = processor.analyze_structure(clean_text)
```

### AIAgent API

```python
# Initialize AI agent
ai_agent = AIAgent(api_key="your_api_key")

# Generate content
content = ai_agent.generate_content(
    text=document_text,
    style="professional"
)

# Structure slides
slides = ai_agent.structure_slides(content)
```

### PPTGenerator API

```python
# Initialize generator
ppt_gen = PPTGenerator()

# Create presentation
ppt_file = ppt_gen.create_presentation(
    content=structured_content,
    style="modern"
)

# Save to file
with open("presentation.pptx", "wb") as f:
    f.write(ppt_file)
```

### ExplanationAgent API

```python
# Initialize explanation agent
exp_agent = ExplanationAgent(api_key="your_api_key")

# Generate explanations
explanations = exp_agent.generate_explanations(
    slide_content=slide_data
)

# Create examples
examples = exp_agent.create_examples(topic="machine learning")
```

---

## Configuration

### Environment Variables

```env
# Required
GEMINI_API_KEY=your_google_gemini_api_key

# Optional
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langchain_key
STREAMLIT_SERVER_ENABLE_FILE_WATCHING=false
```

### Configuration Files

#### `src/config.py`

```python
class Config:
    # AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MAX_TOKENS = 2048
    TEMPERATURE = 0.7
    
    # File Configuration
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt']
    
    # Template Configuration
    DEFAULT_TEMPLATE = 'professional'
    TEMPLATE_STYLES = ['academic', 'modern', 'professional']
```

### Customization

#### AI Prompts

Modify prompts in `src/config.py`:

```python
CONTENT_GENERATION_PROMPT = """
You are an expert presentation creator. Transform the following text into 
a professional presentation with clear structure and engaging content.
"""
```

#### Template Customization

Update templates in `src/ppt_generator.py`:

```python
class CustomTemplate(BaseTemplate):
    def get_color_scheme(self):
        return {
            'primary': '#0066ff',
            'secondary': '#00d4ff',
            'accent': '#ff6b6b'
        }
```

---

## Development Guide

### Setup Development Environment

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd AI-AgentNotesToPPT
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Code Structure

#### Module Organization

```
src/
├── __init__.py
├── config.py              # Configuration and constants
├── document_processor.py  # Document handling
├── ai_agent.py           # AI content generation
├── ppt_generator.py      # PowerPoint creation
└── explanation_agent.py  # Explanation generation
```

#### Coding Standards

- **Python Style**: PEP 8
- **Type Hints**: Required for all functions
- **Documentation**: Docstrings for all classes and methods
- **Error Handling**: Comprehensive try-except blocks

#### Adding New Features

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement Feature**
   - Follow existing patterns
   - Add proper error handling
   - Include type hints
   - Write tests

3. **Test Implementation**
   ```bash
   pytest tests/
   ```

4. **Update Documentation**
   - Update README.md
   - Add API documentation
   - Update configuration guide

### Testing

#### Unit Tests

```python
import unittest
from src.document_processor import DocumentProcessor

class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()
    
    def test_pdf_extraction(self):
        # Test PDF text extraction
        pass
    
    def test_text_cleaning(self):
        # Test text cleaning
        pass
```

#### Integration Tests

```python
import pytest
from src.ai_agent import AIAgent

def test_content_generation():
    agent = AIAgent(api_key="test_key")
    content = agent.generate_content("test text", "professional")
    assert content is not None
```

#### Test Coverage

- Aim for >80% code coverage
- Test all error conditions
- Include performance tests

---

## Deployment

### Local Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_key"

# Run application
streamlit run app.py
```

### Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

#### Docker Compose

```yaml
version: '3.8'
services:
  slidex:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./data:/app/data
```

### Cloud Deployment

#### Streamlit Cloud

1. **Connect GitHub Repository**
2. **Set Environment Variables**
3. **Deploy**

#### Heroku

```bash
# Create Heroku app
heroku create slidex-app

# Set environment variables
heroku config:set GEMINI_API_KEY="your_key"

# Deploy
git push heroku main
```

#### AWS/Azure/GCP

- Use container services
- Set up load balancer
- Configure environment variables
- Monitor performance

---

## Performance Optimization

### Memory Management

#### Document Processing

```python
# Process large documents in chunks
def process_large_document(file_path):
    chunk_size = 1024 * 1024  # 1MB chunks
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            process_chunk(chunk)
```

#### AI Model Optimization

```python
# Batch processing for efficiency
def batch_process_content(content_list):
    batch_size = 5
    results = []
    for i in range(0, len(content_list), batch_size):
        batch = content_list[i:i+batch_size]
        batch_result = process_batch(batch)
        results.extend(batch_result)
    return results
```

### Caching

#### Streamlit Caching

```python
@st.cache_data
def cached_content_generation(text: str, style: str):
    """Cache AI content generation"""
    return ai_agent.generate_content(text, style)

@st.cache_resource
def cached_model_initialization():
    """Cache model initialization"""
    return AIAgent(api_key=Config.GEMINI_API_KEY)
```

#### File Caching

```python
import tempfile
import shutil

class FileCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cached_file(self, file_hash: str):
        cached_path = self.cache_dir / file_hash
        return cached_path if cached_path.exists() else None
```

### Optimization Strategies

1. **Lazy Loading**: Load modules only when needed
2. **Connection Pooling**: Reuse API connections
3. **Async Processing**: Use async for I/O operations
4. **Resource Limits**: Set appropriate timeouts and limits

---

## Troubleshooting

### Common Issues

#### 1. PyTorch Compatibility

**Problem**: RuntimeError with PyTorch classes
**Solution**: 
```bash
streamlit run app.py --server.fileWatcherType none
```

#### 2. API Rate Limits

**Problem**: API quota exceeded
**Solution**: Implement rate limiting and caching

#### 3. Memory Issues

**Problem**: Out of memory with large files
**Solution**: Process files in chunks, implement streaming

#### 4. File Format Errors

**Problem**: Unsupported file formats
**Solution**: Validate file types, provide clear error messages

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug statements
logger.debug(f"Processing file: {file_path}")
logger.debug(f"Extracted text length: {len(text)}")
```

### Performance Monitoring

```python
import time
import psutil

def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        logger.info(f"Function {func.__name__}:")
        logger.info(f"  Time: {end_time - start_time:.2f}s")
        logger.info(f"  Memory: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
        
        return result
    return wrapper
```

---

## Security Considerations

### API Key Management

- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly
- Implement key validation

### File Security

- Validate file types and sizes
- Scan uploaded files for malware
- Use secure temporary storage
- Clean up temporary files

### Data Privacy

- Don't store sensitive data permanently
- Use encryption for data transmission
- Implement data retention policies
- Comply with GDPR/CCPA

---

## Contributing Guidelines

### Pull Request Process

1. **Fork Repository**
2. **Create Feature Branch**
3. **Make Changes**
4. **Add Tests**
5. **Update Documentation**
6. **Submit Pull Request**

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes
- [ ] Performance impact considered

### Release Process

1. **Update Version Number**
2. **Update CHANGELOG**
3. **Create Git Tag**
4. **Deploy to Production**
5. **Monitor Performance**

---

This documentation provides comprehensive technical details for developers working with SlideX. For user-facing documentation, refer to the README.md file.
