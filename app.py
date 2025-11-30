import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
import shutil
from pathlib import Path
import time
import base64
import json
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Import our custom modules
from src.document_processor import DocumentProcessor
from src.ai_agent import AIAgent
from src.ppt_generator import PPTGenerator
from src.explanation_agent import ExplanationAgent
from src.config import Config

# Load environment variables
load_dotenv()

# Fix PyTorch + Streamlit compatibility issue
os.environ['STREAMLIT_SERVER_ENABLE_FILE_WATCHING'] = 'false'

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="SlideX - Professional AI Presentation Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "SlideX - Transform documents into professional presentations with AI"
    }
)

# ==================== PROFESSIONAL STYLING ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');
    
    :root {
        --primary-color: #0066ff;
        --secondary-color: #00d4ff;
        --accent-color: #ff6b6b;
        --success-color: #31a24c;
        --warning-color: #ff9800;
        --danger-color: #f44336;
        --dark-bg: #0f1419;
        --light-bg: #f5f7fa;
        --card-bg: #ffffff;
        --text-primary: #1a1a2e;
        --text-secondary: #616161;
        --border-color: #e0e0e0;
    }
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    code {
        font-family: 'Fira Code', monospace;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    }
    
    /* ==================== HEADER SECTION ==================== */
    .header-container {
        background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0, 102, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .header-content {
        position: relative;
        z-index: 1;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
        margin: 0;
        font-weight: 300;
    }
    
    .status-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 1rem;
    }
    
    /* ==================== CARD STYLES ==================== */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        border-color: var(--primary-color);
    }
    
    .card-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* ==================== UPLOAD SECTION ==================== */
    .upload-container {
        background: linear-gradient(135deg, rgba(0, 102, 255, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%);
        border: 2px dashed var(--primary-color);
        border-radius: 12px;
        padding: 2.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-container:hover {
        border-color: var(--secondary-color);
        background: linear-gradient(135deg, rgba(0, 102, 255, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
    }
    
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .upload-hint {
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    /* ==================== BUTTON STYLES ==================== */
    .stButton > button {
        background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 102, 255, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #31a24c 0%, #4caf50 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(49, 162, 76, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(49, 162, 76, 0.4);
    }
    
    /* ==================== MESSAGE STYLES ==================== */
    .alert {
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .alert-success {
        background: #f0f7f4;
        color: #1e7e74;
        border-color: #31a24c;
    }
    
    .alert-error {
        background: #fef5f5;
        color: #c62e2e;
        border-color: #f44336;
    }
    
    .alert-warning {
        background: #fffaf0;
        color: #e65100;
        border-color: #ff9800;
    }
    
    .alert-info {
        background: #f0f6ff;
        color: #0066ff;
        border-color: #00d4ff;
    }
    
    /* ==================== METRIC CARDS ==================== */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: var(--primary-color);
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 102, 255, 0.15);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ==================== PROGRESS INDICATOR ==================== */
    .progress-item {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding: 1rem;
        background: #f5f7fa;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
    }
    
    .progress-number {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-right: 1rem;
        flex-shrink: 0;
    }
    
    .progress-text {
        color: var(--text-primary);
        font-weight: 500;
    }
    
    /* ==================== SLIDE PREVIEW ==================== */
    .slide-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid var(--primary-color);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .slide-card:hover {
        box-shadow: 0 8px 24px rgba(0, 102, 255, 0.15);
    }
    
    .slide-number {
        display: inline-block;
        background: linear-gradient(135deg, #0066ff 0%, #00d4ff 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .slide-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    .bullet-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .bullet-item {
        padding: 0.5rem 0;
        padding-left: 1.5rem;
        position: relative;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    .bullet-item::before {
        content: "▸";
        position: absolute;
        left: 0;
        color: var(--primary-color);
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .presenter-notes {
        background: #f5f7fa;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        border-left: 4px solid var(--warning-color);
    }
    
    .presenter-notes-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .presenter-notes-content {
        color: var(--text-secondary);
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    /* ==================== EXPLANATION SECTION ==================== */
    .explanation-box {
        background: linear-gradient(135deg, rgba(0, 102, 255, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
    }
    
    .explanation-title {
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .explanation-content {
        color: var(--text-secondary);
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    /* ==================== SIDEBAR STYLES ==================== */
    .sidebar-section {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .sidebar-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .sidebar-content {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* ==================== TABS STYLING ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 1.5rem;
        border-radius: 8px 8px 0 0;
        background: transparent;
        border-bottom: 3px solid transparent;
        color: var(--text-secondary);
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066ff15 0%, #00d4ff15 100%);
        color: var(--primary-color);
        border-bottom-color: var(--primary-color);
    }
    
    /* ==================== FILE INFO ==================== */
    .file-info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .file-info-row:last-child {
        border-bottom: none;
    }
    
    .file-info-label {
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .file-info-value {
        color: var(--text-secondary);
    }
    
    /* ==================== LOADING SPINNER ==================== */
    .loading-text {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    /* ==================== FEATURE LIST ==================== */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .feature-item {
        background: linear-gradient(135deg, rgba(0, 102, 255, 0.05) 0%, rgba(0, 212, 255, 0.05) 100%);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid var(--primary-color);
    }
    
    .feature-item-title {
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .feature-item-desc {
        color: var(--text-secondary);
        font-size: 0.85rem;
        line-height: 1.5;
    }
    
    /* ==================== FOOTER ==================== */
    .footer {
        text-align: center;
        color: var(--text-secondary);
        padding: 2rem;
        border-top: 1px solid var(--border-color);
        margin-top: 3rem;
        font-size: 0.9rem;
    }
    
    .footer-highlight {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    /* ==================== RESPONSIVE ==================== */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.8rem;
        }
        
        .header-subtitle {
            font-size: 0.95rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
    }
    
    /* ==================== HIDE DEFAULT ELEMENTS ==================== */
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    .stDeployButton {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def format_file_size(bytes_size):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} GB"

def create_alert(message, alert_type="info", icon="ℹ️"):
    """Create styled alert message"""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    icon = icons.get(alert_type, "ℹ️")
    st.markdown(f'<div class="alert alert-{alert_type}">{icon} {message}</div>', unsafe_allow_html=True)

def render_progress_step(number, text):
    """Render a progress step"""
    st.markdown(f'''
    <div class="progress-item">
        <div class="progress-number">{number}</div>
        <div class="progress-text">{text}</div>
    </div>
    ''', unsafe_allow_html=True)

# ==================== MAIN APPLICATION ====================

def main():
    # Initialize configuration
    config = Config()
    
    # Initialize session state
    if 'presentation_ready' not in st.session_state:
        st.session_state.presentation_ready = False
        st.session_state.ppt_path = None
        st.session_state.slides = []
        st.session_state.slide_explanations = []
        st.session_state.ppt_info = {}
        st.session_state.processing_complete = False
    
    # Check API key
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_gemini_api_key_here":
        st.markdown('''
        <div class="header-container">
            <div class="header-content">
                <h1 class="header-title">🔐 API Configuration Required</h1>
                <p class="header-subtitle">Set up your Gemini API key to get started</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="card">
            <div class="card-header">Setup Instructions</div>
            <ol style="color: var(--text-primary); line-height: 2;">
                <li>Visit <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a></li>
                <li>Create a new API key</li>
                <li>Copy your key and add it to the <code>.env</code> file:</li>
            </ol>
            <div style="background: #f5f7fa; padding: 1rem; border-radius: 8px; margin-top: 1rem; font-family: 'Fira Code', monospace; color: #0066ff; font-weight: 500;">
                GEMINI_API_KEY=your_api_key_here
            </div>
            <p style="color: var(--text-secondary); margin-top: 1rem; font-size: 0.9rem;">
                Restart the application after adding your API key.
            </p>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    # Initialize components
    doc_processor = DocumentProcessor()
    ai_agent = AIAgent()
    explanation_agent = ExplanationAgent()
    ppt_generator = PPTGenerator()
    
    # ==================== HEADER ====================
    st.markdown('''
    <div class="header-container">
        <div class="header-content">
            <h1 class="header-title">🎯 SlideX</h1>
            <p class="header-subtitle">Professional AI Presentation Generator with Intelligent Explanations</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # ==================== SIDEBAR ====================
    with st.sidebar:
        
        # Quick Info
        st.markdown('''
        <div class="sidebar-section">
            <div class="sidebar-title">✨ Key Features</div>
            <ul style="margin: 0; padding-left: 1.25rem; color: var(--text-secondary); font-size: 0.9rem;">
                <li style="margin-bottom: 0.5rem;">🧠 AI-powered content analysis</li>
                <li style="margin-bottom: 0.5rem;">📊 Professional slide design</li>
                <li style="margin-bottom: 0.5rem;">🔍 Intelligent explanations</li>
                <li style="margin-bottom: 0.5rem;">📝 Presenter notes included</li>
                <li style="margin-bottom: 0.5rem;">⚡ Instant downloads</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
        
        # Support & Resources
        st.markdown('''
        <div class="sidebar-section">
            <div class="sidebar-title">🔗 Resources</div>
            <div class="sidebar-content" style="font-size: 0.9rem;">
                <p>📖 <a href="#documentation">Documentation</a></p>
                <p>💬 <a href="https://github.com/slidex/issues" target="_blank">Report Issues</a></p>
                <p>⭐ <a href="https://github.com/slidex" target="_blank">Star on GitHub</a></p>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # ==================== MAIN CONTENT TABS ====================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Upload & Generate", "📋 Preview", "🔍 Explanations", "❓ Help", "⚙️ Settings"])
    
    # ==================== TAB 1: UPLOAD & GENERATE ====================
    with tab1:
        # Presentation Settings Cards
        st.markdown("### 📊 Presentation Settings")
        
        settings_col1, settings_col2, settings_col3 = st.columns(3, gap="large")
        
        with settings_col1:
            st.markdown('''
            <div class="card">
                <div class="card-header">📑 Slides Configuration</div>
            ''', unsafe_allow_html=True)
            
            max_slides = st.slider(
                "Maximum Slides",
                min_value=5,
                max_value=50,
                value=20,
                step=5,
                help="Set the maximum number of slides to generate",
                label_visibility="collapsed"
            )
            
            st.markdown(f'''
            <div style="margin-top: 1rem; padding: 0.75rem; background: #f0f7f4; border-radius: 6px; text-align: center;">
                <div style="font-size: 0.85rem; color: var(--text-secondary);">Selected</div>
                <div style="font-weight: 700; color: var(--primary-color); font-size: 1.25rem;">{max_slides} Slides</div>
            </div>
            </div>
            ''', unsafe_allow_html=True)
        
        with settings_col2:
            st.markdown('''
            <div class="card">
                <div class="card-header">🎨 Template Style</div>
            ''', unsafe_allow_html=True)
            
            template_style = st.selectbox(
                "Choose Template",
                ["Professional", "Modern", "Academic"],
                help="Choose the presentation template style",
                label_visibility="collapsed",
                index=0
            )
            
            template_descriptions = {
                "Professional": "Corporate, formal, business-focused",
                "Modern": "Contemporary, bold colors, creative",
                "Academic": "Research-focused, technical, formal"
            }
            
            st.markdown(f'''
            <div style="margin-top: 1rem; padding: 0.75rem; background: #f0f7f4; border-radius: 6px;">
                <div style="font-size: 0.9rem; color: var(--text-secondary);">{template_descriptions.get(template_style, "")}</div>
            </div>
            </div>
            ''', unsafe_allow_html=True)
        
        with settings_col3:
            st.markdown('''
            <div class="card">
                <div class="card-header">📖 Explanation Details</div>
            ''', unsafe_allow_html=True)
            
            explanation_detail = st.selectbox(
                "Detail Level",
                ["Basic", "Standard", "Detailed"],
                help="Choose the depth of explanations",
                label_visibility="collapsed",
                index=1
            )
            
            detail_descriptions = {
                "Basic": "Minimal explanations",
                "Standard": "Recommended, balanced",
                "Detailed": "Comprehensive analysis"
            }
            
            st.markdown(f'''
            <div style="margin-top: 1rem; padding: 0.75rem; background: #f0f7f4; border-radius: 6px;">
                <div style="font-size: 0.9rem; color: var(--text-secondary);">{detail_descriptions.get(explanation_detail, "")}</div>
            </div>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Initialize variables
        uploaded_file = None
        text_content = None
        temp_file_path = None
        
        # Custom CSS for input elements
        st.markdown('''
        <style>
            textarea {
                background-color: #f5f7fa !important;
                border: 1px solid #e0e6ed !important;
                color: var(--text-primary) !important;
            }
            textarea:focus {
                background-color: #f5f7fa !important;
                border: 2px solid var(--primary-color) !important;
                box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1) !important;
            }
            [data-testid="stFileUploadDropzone"] {
                background-color: #f5f7fa !important;
                border: 2px dashed #00d4ff !important;
                padding: 2rem !important;
            }
            button[kind="secondary"] {
                background-color: var(--primary-color) !important;
                color: white !important;
                border: none !important;
                border-radius: 6px !important;
            }
            button[kind="secondary"]:hover {
                background-color: #0052cc !important;
            }
        </style>
        ''', unsafe_allow_html=True)
        
        st.markdown("### 📝 Input Your Content")
        st.markdown("Choose one or both methods to provide your content:")
        
        # Two column layout - Text Input and File Upload
        input_col1, input_col2 = st.columns(2, gap="large")
        
        with input_col1:
            st.markdown('''
            <div class="card input-card">
                <div class="card-header">✍️ Paste Text</div>
            ''', unsafe_allow_html=True)
            
            text_content = st.text_area(
                "Enter your text content",
                placeholder="Paste your notes, article, research paper, or any text content here...",
                height=200,
                help="Paste your content directly",
                label_visibility="collapsed"
            )
            
            if text_content and text_content.strip():
                char_count = len(text_content)
                st.markdown(f'''
                <div style="margin-top: 1rem; padding: 0.75rem; background: #e8ecf1; border-radius: 6px; text-align: center; border-left: 4px solid var(--primary-color);">
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">✅ Content Ready</div>
                    <div style="font-weight: 700; color: var(--primary-color); font-size: 1.1rem;">{char_count:,} characters</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        
        with input_col2:
            st.markdown('''
            <div class="card input-card">
                <div class="card-header">📤 Upload File</div>
            ''', unsafe_allow_html=True)
            
            st.markdown('''
            <div class="file-uploader-wrapper" style="border: 2px dashed #00d4ff; border-radius: 12px; text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem;">Drag & Drop</div>
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">or click to browse</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">PDF, DOCX, TXT • up to 50MB</div>
            </div>
            ''', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choose file",
                type=['pdf', 'txt', 'docx'],
                help="Upload your document (PDF, DOCX, or TXT)",
                label_visibility="collapsed"
            )
            
            if uploaded_file is not None:
                file_size = uploaded_file.size / 1024 / 1024  # Convert to MB
                st.markdown(f'''
                <div style="margin-top: 1rem; padding: 0.75rem; background: #e8ecf1; border-radius: 6px; text-align: center; border-left: 4px solid var(--primary-color);">
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">✅ File Selected</div>
                    <div style="font-weight: 700; color: var(--primary-color); font-size: 1.1rem;">{uploaded_file.name}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">{file_size:.2f} MB</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate Button (Shows when file or text is provided)
        st.markdown('<br>', unsafe_allow_html=True)
        
        if uploaded_file is not None or (text_content and text_content.strip()):
            col_btn1, col_btn2 = st.columns([2, 1])
            with col_btn1:
                generate_btn = st.button("🚀 Generate Presentation", key="generate_btn", use_container_width=True)
            
            if generate_btn:
                # Determine content source
                if uploaded_file is not None:
                    # Process uploaded file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        temp_file_path = temp_file.name
                    
                    file_extension = f".{uploaded_file.name.split('.')[-1]}"
                    
                    # Processing steps
                    st.markdown('''
                    <div class="card">
                        <div class="card-header">🔄 Processing Your Document</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Step 1: Extract
                    render_progress_step(1, "Extracting text from document...")
                    text = doc_processor.extract_text(temp_file_path, file_extension)
                    
                    if not text:
                        create_alert("Could not extract text from the document. Please try a different file.", "error")
                        st.stop()
                    
                    create_alert(f"Successfully extracted {len(text):,} characters from document", "success")
                
                else:
                    # Use pasted text
                    text = text_content
                    st.markdown('''
                    <div class="card">
                        <div class="card-header">🔄 Processing Your Text</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    render_progress_step(1, "Processing text content...")
                    create_alert(f"Text content loaded: {len(text):,} characters", "success")
                
                try:
                    # Step 2: Generate outline
                    render_progress_step(2, "Analyzing content and generating slide structure...")
                    slide_outline = ai_agent.generate_slide_outline(text, max_slides)
                    create_alert(f"Generated outline for {len(slide_outline)} slides", "success")
                    
                    # Step 3: Generate content
                    render_progress_step(3, "Generating detailed slide content with AI...")
                    slides = ai_agent.generate_slide_content(slide_outline, text)
                    create_alert(f"Generated content for {len(slides)} slides", "success")
                    
                    # Step 4: Generate explanations
                    render_progress_step(4, "Creating intelligent explanations...")
                    slide_explanations = []
                    for i, slide in enumerate(slides):
                        explanation = explanation_agent.generate_slide_explanation(slide, text[:1000])
                        slide_explanations.append(explanation)
                    
                    create_alert(f"Generated explanations for all {len(slides)} slides", "success")
                    
                    # Step 5: Create PowerPoint
                    render_progress_step(5, "Building PowerPoint presentation...")
                    ppt_path = ppt_generator.create_presentation(slides, template_style.lower())
                    
                    # Get presentation info
                    ppt_info = ppt_generator.get_presentation_info(ppt_path)
                    
                    # Store in session
                    st.session_state.presentation_ready = True
                    st.session_state.ppt_path = ppt_path
                    st.session_state.slides = slides
                    st.session_state.slide_explanations = slide_explanations
                    st.session_state.ppt_info = ppt_info
                    st.session_state.processing_complete = True
                    
                    create_alert("✨ Presentation created successfully! Check the Preview tab.", "success")
                    
                    # Display metrics
                    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
                    
                    metric_cols = st.columns(4)
                    with metric_cols[0]:
                        st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-value">{len(slides)}</div>
                            <div class="metric-label">Slides Generated</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with metric_cols[1]:
                        st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-value">{len(text)//100}</div>
                            <div class="metric-label">Content Units</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with metric_cols[2]:
                        st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-value">~{(len(slides) * 2)}</div>
                            <div class="metric-label">Minutes Duration</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with metric_cols[3]:
                        st.markdown(f'''
                        <div class="metric-card">
                            <div class="metric-value">{template_style}</div>
                            <div class="metric-label">Template Used</div>
                        </div>
                        ''', unsafe_allow_html=True)
                
                except Exception as e:
                    create_alert(f"Error during processing: {str(e)}", "error")
                    create_alert("Please check your API key configuration and try again.", "warning")
                    st.error(f"Debug info: {str(e)}")
                
                finally:
                    if uploaded_file is not None:
                        try:
                            if os.path.exists(temp_file_path):
                                os.unlink(temp_file_path)
                        except:
                            pass
            else:
                st.markdown('''
                <div class="card" style="text-align: center;">
                    <p style="color: var(--text-secondary); margin: 0;">
                        👆 Please upload a file to get started
                    </p>
                </div>
                ''', unsafe_allow_html=True)
    
    # ==================== TAB 2: PREVIEW ====================
    with tab2:
        if st.session_state.get("presentation_ready", False):
            slides = st.session_state.get("slides", [])
            ppt_info = st.session_state.get("ppt_info", {})
            
            if slides:
                # Download Section
                st.markdown('<div class="card"><div class="card-header">📥 Download Your Presentation</div>', unsafe_allow_html=True)
                
                ppt_path = st.session_state.get("ppt_path")
                if ppt_path and os.path.exists(ppt_path):
                    with open(ppt_path, "rb") as file:
                        st.download_button(
                            label="📥 Download PowerPoint (.pptx)",
                            data=file.read(),
                            file_name=f"slidex_presentation_{int(time.time())}.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            use_container_width=True
                        )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Metrics
                st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
                
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-value">{len(slides)}</div>
                        <div class="metric-label">Total Slides</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with metric_cols[1]:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-value">{ppt_info.get("file_size_mb", 0):.1f}MB</div>
                        <div class="metric-label">File Size</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with metric_cols[2]:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-value">{datetime.now().strftime("%H:%M")}</div>
                        <div class="metric-label">Generated At</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with metric_cols[3]:
                    st.markdown(f'''
                    <div class="metric-card">
                        <div class="metric-value">{ppt_info.get("template_style", "Professional")}</div>
                        <div class="metric-label">Template</div>
                    </div>
                    ''', unsafe_allow_html=True)
                
                # Slide Preview
                st.markdown('''
                <div style="margin-top: 2rem;">
                    <div class="card">
                        <div class="card-header">📋 Slide Preview</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                for i, slide in enumerate(slides[:10]):
                    with st.expander(f"🎯 Slide {i+1}: {slide.get('title', 'Untitled')}", expanded=(i==0)):
                        st.markdown(f'''
                        <div class="slide-card">
                            <div class="slide-number">SLIDE {i+1}</div>
                            <div class="slide-title">{slide.get("title", "Untitled")}</div>
                        ''', unsafe_allow_html=True)
                        
                        bullet_points = slide.get("bullet_points", [])
                        if bullet_points:
                            st.markdown('<ul class="bullet-list">', unsafe_allow_html=True)
                            for point in bullet_points:
                                st.markdown(f'<li class="bullet-item">{point}</li>', unsafe_allow_html=True)
                            st.markdown('</ul>', unsafe_allow_html=True)
                        
                        notes = slide.get("presenter_notes", "")
                        if notes:
                            st.markdown(f'''
                            <div class="presenter-notes">
                                <div class="presenter-notes-title">📝 Presenter Notes</div>
                                <div class="presenter-notes-content">{notes}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                if len(slides) > 10:
                    st.markdown(f'''
                    <div class="card" style="text-align: center; margin-top: 1rem;">
                        <p style="color: var(--text-secondary); margin: 0;">
                            ... and {len(slides) - 10} more slides
                        </p>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="card" style="text-align: center; padding: 3rem;">
                <p style="font-size: 1.1rem; color: var(--text-secondary); margin: 0;">
                    👈 Generate a presentation first to see the preview
                </p>
            </div>
            ''', unsafe_allow_html=True)
    
    # ==================== TAB 3: EXPLANATIONS ====================
    with tab3:
        if st.session_state.get("presentation_ready", False):
            slides = st.session_state.get("slides", [])
            slide_explanations = st.session_state.get("slide_explanations", [])
            
            if slides and slide_explanations:
                st.markdown('''
                <div class="card">
                    <div class="card-header">🧠 Intelligent Slide Explanations</div>
                    <p style="color: var(--text-secondary); margin-top: 0.5rem;">
                        Each slide is accompanied by comprehensive explanations to help you understand and present the content effectively.
                    </p>
                </div>
                ''', unsafe_allow_html=True)
                
                for i, (slide, explanation) in enumerate(zip(slides[:10], slide_explanations[:10])):
                    with st.expander(f"🔍 Slide {i+1}: {slide.get('title', 'Untitled')}", expanded=(i==0)):
                        if explanation.get("explanation"):
                            st.markdown(f'''
                            <div class="explanation-box">
                                <div class="explanation-title">📖 Understanding</div>
                                <div class="explanation-content">{explanation["explanation"]}</div>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        if explanation.get("examples"):
                            st.markdown(f'''
                            <div class="explanation-box">
                                <div class="explanation-title">💡 Examples</div>
                            ''', unsafe_allow_html=True)
                            
                            for example in explanation["examples"][:3]:
                                st.markdown(f'<div class="explanation-content">• {example}</div>', unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        if explanation.get("questions"):
                            st.markdown(f'''
                            <div class="explanation-box">
                                <div class="explanation-title">❓ Expected Questions</div>
                            ''', unsafe_allow_html=True)
                            
                            for question in explanation["questions"][:3]:
                                st.markdown(f'<div class="explanation-content">• {question}</div>', unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div class="card" style="text-align: center; padding: 3rem;">
                <p style="font-size: 1.1rem; color: var(--text-secondary); margin: 0;">
                    👈 Generate a presentation to see intelligent explanations
                </p>
            </div>
            ''', unsafe_allow_html=True)
    
    # ==================== TAB 4: HELP ====================
    with tab4:
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown('''
            <div class="card">
                <div class="card-header">🚀 Getting Started</div>
                <ol style="color: var(--text-secondary); line-height: 1.8;">
                    <li><strong>Upload:</strong> Choose a PDF, TXT, or DOCX file</li>
                    <li><strong>Configure:</strong> Set presentation parameters in the sidebar</li>
                    <li><strong>Generate:</strong> Click "Generate Presentation"</li>
                    <li><strong>Preview:</strong> Review slides and explanations</li>
                    <li><strong>Download:</strong> Get your PowerPoint file</li>
                </ol>
            </div>
            
            <div class="card">
                <div class="card-header">📄 Supported Formats</div>
                <div class="feature-grid">
                    <div class="feature-item">
                        <div class="feature-item-title">📕 PDF</div>
                        <div class="feature-item-desc">Research papers, publications, scanned documents</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-item-title">📄 Text</div>
                        <div class="feature-item-desc">Plain text files, notes, articles</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-item-title">📗 Word</div>
                        <div class="feature-item-desc">DOCX files, formatted documents</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown('''
            <div class="card">
                <div class="card-header">✨ Key Features</div>
                <div class="feature-grid" style="grid-template-columns: 1fr;">
                    <div class="feature-item">
                        <div class="feature-item-title">🧠 Intelligent Analysis</div>
                        <div class="feature-item-desc">AI understands content and creates logical structures</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-item-title">📊 Professional Design</div>
                        <div class="feature-item-desc">Multiple templates with modern styling</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-item-title">🔍 Explanations</div>
                        <div class="feature-item-desc">Comprehensive context for each slide</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-item-title">⚡ Instant Export</div>
                        <div class="feature-item-desc">Download fully editable PowerPoint presentations</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">❓ FAQ</div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    <p><strong>Can I edit the presentation after download?</strong><br>
                    Yes, all presentations are fully editable in PowerPoint.</p>
                    <p style="margin-top: 1rem;"><strong>What's the file size limit?</strong><br>
                    Maximum 50MB for uploads.</p>
                    <p style="margin-top: 1rem;"><strong>How long does generation take?</strong><br>
                    Usually 1-3 minutes depending on document length.</p>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    # ==================== TAB 5: SETTINGS ====================
    with tab5:
        st.markdown('''
        <div class="settings-header">
            <h2 style="margin: 0;">⚙️ Personal Settings & Configuration</h2>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">Customize your SlideX experience</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Settings in tabs
        settings_tab1, settings_tab2, settings_tab3 = st.tabs(
            ["💾 Preferences", "🎨 Display", "📥 Export"]
        )
        
        # Preferences Tab
        with settings_tab1:
            st.markdown("### 💾 Default Preferences")
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("#### Presentation Defaults")
                default_max = st.slider(
                    "Default Maximum Slides",
                    5, 50, 20,
                    step=5,
                    help="Slides to generate by default"
                )
                
                default_template = st.selectbox(
                    "Default Template",
                    ["Professional", "Modern", "Academic"],
                    help="Your preferred presentation style"
                )
            
            with col2:
                st.markdown("#### Processing Defaults")
                default_mode = st.radio(
                    "Processing Mode",
                    ["⚡ Fast", "⚖️ Balanced", "🎯 Quality"],
                    help="Fast: Speed over accuracy | Balanced: Recommended | Quality: Best accuracy"
                )
                
                default_detail = st.selectbox(
                    "Explanation Detail Level",
                    ["📄 Basic", "📖 Standard", "📚 Detailed"],
                    help="Depth of slide explanations"
                )
            
            st.markdown("---")
            st.markdown("#### Processing Options")
            
            col1, col2 = st.columns(2)
            with col1:
                include_examples = st.checkbox("Include Real-World Examples", value=True)
                include_questions = st.checkbox("Include Q&A Section", value=True)
            with col2:
                include_resources = st.checkbox("Include Resource Recommendations", value=True)
                include_notes = st.checkbox("Include Presenter Notes", value=True)
            
            if st.button("💾 Save Preferences", use_container_width=True):
                st.success("✅ Your preferences have been saved!")
        
        # Display Settings Tab
        with settings_tab2:
            st.markdown("### 🎨 Display & Theme Settings")
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("#### Theme Selection")
                theme = st.radio(
                    "Color Theme",
                    ["☀️ Light", "🌙 Dark", "🔄 Auto (System)"],
                    help="Choose your preferred color scheme"
                )
                
                font_size = st.slider(
                    "UI Font Size",
                    70, 130, 100,
                    format="%d%%",
                    help="Adjust text size across the interface"
                )
            
            with col2:
                st.markdown("#### Layout Options")
                compact = st.checkbox("Compact Mode", value=False, help="Reduce spacing between elements")
                wide_layout = st.checkbox("Wide Layout", value=False, help="Use full screen width")
                sidebar_collapsed = st.checkbox("Collapse Sidebar on Startup", value=False)
            
            st.markdown("---")
            st.markdown("#### Language & Localization")
            
            language = st.selectbox(
                "Interface Language",
                ["English", "Spanish", "French", "German", "Chinese", "Japanese"]
            )
            
            timezone = st.selectbox(
                "Timezone",
                ["UTC", "EST", "CST", "MST", "PST", "IST", "GST", "Custom"]
            )
            
            st.markdown("---")
            st.markdown("#### Preview")
            st.markdown(f"""
            <div class="card">
                <div style="font-size: {font_size}%; color: var(--text-secondary);">
                    This is a preview of your selected theme and font size.
                    <br><strong style="color: var(--primary-color);">Your customizations look great!</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💾 Save Display Settings", use_container_width=True):
                st.success("✅ Display settings updated!")
        
        # Export Settings Tab
        with settings_tab3:
            st.markdown("### 📥 Export & Download Settings")
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("#### File Format & Quality")
                file_format = st.radio(
                    "Export Format",
                    ["📊 PowerPoint (.pptx)", "🖼️ PDF (Preview)", "📄 Outline Only"]
                )
                
                quality = st.selectbox(
                    "Export Quality",
                    ["Draft", "Standard", "High Quality", "Maximum (Large Files)"]
                )
            
            with col2:
                st.markdown("#### Download Options")
                auto_download = st.checkbox(
                    "Auto-Download on Generation",
                    value=True,
                    help="Automatically download after processing"
                )
                
                compression = st.checkbox(
                    "Enable Compression",
                    value=False,
                    help="Reduce file size (slight quality loss)"
                )
                
                open_after_download = st.checkbox(
                    "Open File After Download",
                    value=False,
                    help="Automatically open in default app"
                )
            
            st.markdown("---")
            st.markdown("#### File Naming")
            
            naming_template = st.text_input(
                "Filename Template",
                "SlideX_{date}_{time}",
                help="Available: {date}, {time}, {title}, {timestamp}"
            )
            
            st.info("""
            💡 **Example formats:**
            - `SlideX_{date}` → `SlideX_2025-11-27`
            - `Presentation_{title}` → `Presentation_MyNotes`
            - `Export_{timestamp}` → `Export_1732696800`
            """)
            
            st.markdown("---")
            st.markdown("#### Batch Export")
            
            batch_size = st.slider(
                "Batch Processing Size",
                1, 10, 3,
                help="Number of files to process simultaneously"
            )
            
            if st.button("📁 Choose Default Download Folder", use_container_width=True):
                st.info("📂 Default: Downloads folder (system setting)")
            
            if st.button("💾 Save Export Settings", use_container_width=True):
                st.success("✅ Export settings saved!")
        
        st.markdown("---")
        
        # Reset & Backup
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Export Settings", use_container_width=True):
                st.success("✅ Settings exported to clipboard!")
        with col2:
            if st.button("📥 Import Settings", use_container_width=True):
                st.info("📋 Paste your settings JSON to import")
        with col3:
            if st.button("🔄 Reset All", use_container_width=True):
                st.warning("⚠️ All settings reset to defaults!")
    
    # ==================== FOOTER ====================
    st.markdown('''
    <div class="footer">
        <p>
            <span class="footer-highlight">🎯 SlideX</span> — Professional AI Presentation Generator
        </p>
        <p>
            Built with <span class="footer-highlight">Streamlit</span>
        </p>
        <p style="margin-top: 1rem; font-size: 0.8rem;">
            © 2025 SlideX. All rights reserved.
        </p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
