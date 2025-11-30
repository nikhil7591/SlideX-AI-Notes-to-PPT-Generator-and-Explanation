# SlideX - AI Presentation Generator 🎯

Transform your documents into professional PowerPoint presentations with AI-powered content generation and intelligent explanations.

## ✨ Features

- **🤖 AI-Powered Content Generation**: Advanced document processing with Google Gemini AI
- **📊 Professional Slide Design**: Multiple template styles (Academic, Modern, Professional)
- **🧠 Intelligent Explanations**: Detailed explanations for each slide with examples
- **📝 Multi-Format Support**: PDF, DOCX, TXT files
- **🎨 Beautiful UI**: Modern glass-morphism design with Streamlit
- **⚡ Real-time Processing**: Fast and efficient document analysis
- **💾 Export Ready**: Download professional PowerPoint files

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-AgentNotesToPPT
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google Gemini API key
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Fix for PyTorch + Streamlit Compatibility

If you encounter PyTorch compatibility issues, the app includes a fix. Alternatively, run with:
```bash
streamlit run app.py --server.fileWatcherType none
```

## 📁 Project Structure

```
SlideX/
├── app.py                 # Main Streamlit application
├── src/                   # Source modules
│   ├── ai_agent.py        # AI content generation
│   ├── document_processor.py  # Document parsing
│   ├── ppt_generator.py   # PowerPoint creation
│   ├── explanation_agent.py   # Intelligent explanations
│   └── config.py          # Configuration and prompts
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🎯 Core Components

### 1. Document Processor (`src/document_processor.py`)
- Supports PDF, DOCX, and TXT files
- Advanced text extraction and cleaning
- Content structure analysis

### 2. AI Agent (`src/ai_agent.py`)
- Powered by Google Gemini AI
- Intelligent content structuring
- Multiple AI model support (LangChain + Direct Gemini)

### 3. PowerPoint Generator (`src/ppt_generator.py`)
- Professional template designs
- Automatic slide layout optimization
- Rich formatting and styling

### 4. Explanation Agent (`src/explanation_agent.py`)
- Detailed slide explanations
- Real-world examples and analogies
- Discussion questions and resources
- Presentation summary generation

## 🎨 Template Styles

### Academic Template
- Clean, professional design
- Perfect for educational presentations
- Structured layout with clear hierarchy

### Modern Template
- Contemporary design elements
- Bold colors and modern typography
- Ideal for business presentations

### Professional Template
- Corporate-friendly design
- Subtle colors and professional styling
- Suitable for formal presentations

## 🛠️ Configuration

### Environment Variables

Create a `.env` file with:

```env
# Required
GEMINI_API_KEY=your_google_gemini_api_key

# Optional
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langchain_key
```

### Customization

You can customize:
- AI prompts in `src/config.py`
- Template styles in `src/ppt_generator.py`
- UI elements in `app.py`

## 📖 Usage Guide

1. **Launch the application**: Run `streamlit run app.py`
2. **Upload your document**: Choose PDF, DOCX, or TXT file
3. **Select template**: Choose from Academic, Modern, or Professional
4. **Generate presentation**: Click "Generate Presentation" 
5. **View explanations**: Check the "Explanations" tab for detailed insights
6. **Download**: Get your PowerPoint file

## 🤖 AI Features

### Content Generation
- Automatic topic identification
- Logical slide sequencing
- Key point extraction
- Professional language generation

### Explanation System
- **Slide Explanations**: Detailed breakdown of each slide
- **Real-World Examples**: Practical applications and analogies
- **Key Terminology**: Important terms and definitions
- **Discussion Questions**: Interactive engagement prompts
- **Learning Resources**: Additional reading suggestions
- **Presentation Summary**: Comprehensive overview

## 🔧 Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **python-pptx**: PowerPoint file creation
- **Google Generative AI**: AI content generation
- **LangChain**: AI framework integration
- **PyPDF2/python-docx**: Document processing
- **NLTK/spacy**: Natural language processing

### Architecture
- **Modular Design**: Separate components for easy maintenance
- **Error Handling**: Comprehensive error management
- **Fallback Systems**: Multiple AI model support
- **Performance Optimized**: Efficient processing pipeline

## 🐛 Troubleshooting

### Common Issues

1. **PyTorch Compatibility Error**
   - Solution: Use `streamlit run app.py --server.fileWatcherType none`
   - The app includes automatic fix in code

2. **API Key Issues**
   - Ensure `.env` file is properly configured
   - Check Google Gemini API key validity

3. **Document Processing Errors**
   - Supported formats: PDF, DOCX, TXT
   - File size limit: 50MB
   - Ensure documents are not password-protected

4. **Memory Issues**
   - Large documents may require more RAM
   - Consider splitting large documents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for powerful content generation
- Streamlit for the amazing web framework
- python-pptx for PowerPoint file creation
- LangChain for AI framework integration

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**SlideX** - Transform your ideas into stunning presentations with AI 🚀
