"""
PowerPoint Generation Module
Creates PowerPoint presentations from AI-generated content
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import tempfile

# PowerPoint library
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Local imports
from .config import Config, PRESENTATION_TEMPLATES

class PPTGenerator:
    """Generates PowerPoint presentations from AI-generated content"""
    
    def __init__(self, template_style: str = "professional"):
        """
        Initialize PPT Generator
        
        Args:
            template_style: Template style to use for the presentation
        """
        self.config = Config()
        self.template_style = template_style
        self.template_config = PRESENTATION_TEMPLATES.get(template_style, PRESENTATION_TEMPLATES["professional"])
    
    def create_presentation(self, slides_data: List[Dict[str, Any]], output_path: Optional[str] = None) -> str:
        """
        Create a PowerPoint presentation from slide data
        
        Args:
            slides_data: List of slide data with titles, bullet points, and notes
            output_path: Path to save the presentation (if None, creates temp file)
            
        Returns:
            Path to the created presentation file
        """
        try:
            # Create new presentation
            prs = Presentation()
            
            # Apply template settings
            self._apply_template_settings(prs)
            
            # Add title slide
            if slides_data:
                self._add_title_slide(prs, slides_data[0])
            
            # Add content slides
            for i, slide_data in enumerate(slides_data[1:], 1):
                self._add_content_slide(prs, slide_data, i)
            
            # Save presentation
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(tempfile.gettempdir(), f"presentation_{timestamp}.pptx")
            
            prs.save(output_path)
            return output_path
            
        except Exception as e:
            print(f"Error creating presentation: {e}")
            raise
    
    def _apply_template_settings(self, prs: Presentation):
        """Apply template settings to the presentation"""
        try:
            # Set slide dimensions for standard 16:9
            prs.slide_width = Inches(10)
            prs.slide_height = Inches(7.5)
            
            # Apply background color to slide master
            slide_master = prs.slide_master
            background = slide_master.background
            fill = background.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(255, 255, 255)  # White background for professional look

            # Apply font settings to slide master
            for slide_layout in slide_master.slide_layouts:
                for shape in slide_layout.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            font = paragraph.font
                            font.name = self.template_config["body_font"]
                            font.size = Pt(self.template_config["body_size"])
                            font.color.rgb = RGBColor(64, 64, 64)  # Default dark gray
        except Exception as e:
            print(f"Error applying template settings: {e}")
    
    def _add_title_slide(self, prs: Presentation, first_slide_data: Dict[str, Any]):
        """Add a professional title slide with improved layout"""
        try:
            # Use blank layout for maximum customization
            slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Add gradient-like header bar
            header_shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(0), Inches(0),
                Inches(10), Inches(3)
            )
            header_shape.fill.solid()
            header_shape.fill.fore_color.rgb = RGBColor(*self._hex_to_rgb(self.template_config["theme_color"]))
            header_shape.line.color.rgb = RGBColor(*self._hex_to_rgb(self.template_config["theme_color"]))
            
            # Add title
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.8), Inches(9), Inches(1.5))
            title_frame = title_box.text_frame
            title_frame.text = first_slide_data.get("title", "AI Generated Presentation")
            title_frame.word_wrap = True
            
            paragraph = title_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.CENTER
            font = paragraph.font
            font.name = self.template_config["title_font"]
            font.size = Pt(54)
            font.bold = True
            font.color.rgb = RGBColor(255, 255, 255)  # White text
            
            # Add subtitle
            subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(3.5), Inches(8), Inches(1))
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.text = "Professional Presentation"
            
            paragraph = subtitle_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.CENTER
            font = paragraph.font
            font.name = self.template_config["body_font"]
            font.size = Pt(28)
            font.color.rgb = RGBColor(100, 100, 100)
            
            # Add date
            date_box = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(8), Inches(1))
            date_frame = date_box.text_frame
            date_frame.text = f"Generated on {datetime.now().strftime('%B %d, %Y')}"
            
            paragraph = date_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.CENTER
            font = paragraph.font
            font.name = self.template_config["body_font"]
            font.size = Pt(16)
            font.italic = True
            font.color.rgb = RGBColor(128, 128, 128)
                
        except Exception as e:
            print(f"Error adding title slide: {e}")
            # Fallback: create a basic slide
            self._add_fallback_title_slide(prs)
    
    def _add_content_slide(self, prs: Presentation, slide_data: Dict[str, Any], slide_number: int):
        """Add a professional content slide with improved layout and formatting"""
        try:
            # Use blank layout for maximum customization
            slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Add header bar with theme color
            header_shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(0), Inches(0),
                Inches(10), Inches(0.8)
            )
            header_shape.fill.solid()
            header_shape.fill.fore_color.rgb = RGBColor(*self._hex_to_rgb(self.template_config["theme_color"]))
            header_shape.line.fill.background()
            
            # Set title with white text on colored background
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(8.5), Inches(0.5))
            title_frame = title_box.text_frame
            title_frame.text = slide_data.get("title", f"Slide {slide_number}")
            title_frame.word_wrap = True
            
            paragraph = title_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.LEFT
            font = paragraph.font
            font.name = self.template_config["title_font"]
            font.size = Pt(32)
            font.bold = True
            font.color.rgb = RGBColor(255, 255, 255)  # White text
            
            # Add slide number in header
            slide_num_box = slide.shapes.add_textbox(Inches(9), Inches(0.2), Inches(0.8), Inches(0.4))
            slide_num_frame = slide_num_box.text_frame
            slide_num_frame.text = str(slide_number)
            
            para = slide_num_frame.paragraphs[0]
            para.alignment = PP_ALIGN.RIGHT
            para.font.size = Pt(14)
            para.font.bold = True
            para.font.color.rgb = RGBColor(255, 255, 255)
            
            # Add content area with left border
            left_border = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(0), Inches(0.8),
                Inches(0.08), Inches(6.7)
            )
            left_border.fill.solid()
            left_border.fill.fore_color.rgb = RGBColor(*self._hex_to_rgb(self.template_config["theme_color"]))
            left_border.line.fill.background()
            
            # Add bullet points with professional formatting
            bullet_points = slide_data.get("bullet_points", [])
            if bullet_points:
                self._add_bullet_points(slide, bullet_points)
            
            # Add presenter notes
            presenter_notes = slide_data.get("presenter_notes", "")
            if presenter_notes:
                self._add_presenter_notes(slide, presenter_notes)
                
        except Exception as e:
            print(f"Error adding content slide {slide_number}: {e}")
            # Fallback: create a basic slide
            self._add_fallback_content_slide(prs, slide_data, slide_number)
    
    def _add_bullet_points(self, slide, bullet_points: List[str]):
        """Add bullet points to a slide with professional formatting"""
        try:
            # Create a text box for bullet points with proper margins
            left = Inches(0.8)
            top = Inches(1.5)
            width = Inches(8.5)
            height = Inches(5.2)
            
            content_shape = slide.shapes.add_textbox(left, top, width, height)
            text_frame = content_shape.text_frame
            text_frame.clear()
            text_frame.word_wrap = True
            
            # Add bullet points with professional styling
            for i, point in enumerate(bullet_points[:6]):  # Limit to 6 bullet points
                if i == 0:
                    p = text_frame.paragraphs[0]
                else:
                    p = text_frame.add_paragraph()
                
                p.text = point.strip()
                p.level = 0  # Bullet level
                p.alignment = PP_ALIGN.LEFT
                p.space_before = Pt(8)
                p.space_after = Pt(8)
                
                # Format bullet point with professional appearance
                font = p.font
                font.name = self.template_config["body_font"]
                font.size = Pt(self.template_config["body_size"])
                font.color.rgb = RGBColor(50, 50, 50)  # Darker text for readability
                font.bold = False
                
                # Set bullet style
                p.font.bold = False
                
        except Exception as e:
            print(f"Error adding bullet points: {e}")
    
    def _add_presenter_notes(self, slide, notes_text: str):
        """Add presenter notes to a slide"""
        try:
            # Add notes to the slide's notes page
            notes_slide = slide.notes_slide
            notes_text_frame = notes_slide.notes_text_frame
            notes_text_frame.text = notes_text
            
            # Format notes text
            if notes_text_frame.paragraphs:
                for paragraph in notes_text_frame.paragraphs:
                    self._format_notes_paragraph(paragraph)
                    
        except Exception as e:
            print(f"Error adding presenter notes: {e}")
    
    def _format_title(self, title_shape):
        """Format the title text"""
        try:
            if title_shape and hasattr(title_shape, 'text_frame'):
                text_frame = title_shape.text_frame
                if text_frame.paragraphs:
                    paragraph = text_frame.paragraphs[0]
                    
                    # Font settings
                    font = paragraph.font
                    font.name = self.template_config["title_font"]
                    font.size = Pt(self.template_config["title_size"])
                    font.bold = True
                    
                    # Color
                    if hasattr(font, 'color'):
                        font.color.rgb = RGBColor(*self._hex_to_rgb(self.template_config["theme_color"]))
                    
                    # Alignment
                    paragraph.alignment = PP_ALIGN.CENTER
                    
        except Exception as e:
            print(f"Error formatting title: {e}")
    
    def _format_subtitle(self, subtitle_shape):
        """Format the subtitle text"""
        try:
            if subtitle_shape and hasattr(subtitle_shape, 'text_frame'):
                text_frame = subtitle_shape.text_frame
                if text_frame.paragraphs:
                    paragraph = text_frame.paragraphs[0]
                    
                    # Font settings
                    font = paragraph.font
                    font.name = self.template_config["body_font"]
                    font.size = Pt(self.template_config["body_size"] - 4)
                    font.italic = True
                    
                    # Color
                    if hasattr(font, 'color'):
                        font.color.rgb = RGBColor(128, 128, 128)  # Gray color
                    
                    # Alignment
                    paragraph.alignment = PP_ALIGN.CENTER
                    
        except Exception as e:
            print(f"Error formatting subtitle: {e}")
    
    def _format_bullet_point(self, paragraph):
        """Format bullet point text"""
        try:
            # Font settings
            font = paragraph.font
            font.name = self.template_config["body_font"]
            font.size = Pt(self.template_config["body_size"])
            
            # Color
            if hasattr(font, 'color'):
                font.color.rgb = RGBColor(64, 64, 64)  # Dark gray
            
            # Auto size
            if hasattr(paragraph, 'auto_size'):
                paragraph.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
                
        except Exception as e:
            print(f"Error formatting bullet point: {e}")
    
    def _format_notes_paragraph(self, paragraph):
        """Format presenter notes paragraph"""
        try:
            # Font settings
            font = paragraph.font
            font.name = "Calibri"
            font.size = Pt(12)
            
            # Color
            if hasattr(font, 'color'):
                font.color.rgb = RGBColor(64, 64, 64)  # Dark gray
                
        except Exception as e:
            print(f"Error formatting notes paragraph: {e}")
    
    def _add_fallback_title_slide(self, prs: Presentation):
        """Add a basic title slide as fallback"""
        try:
            slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Add title text box
            left = Inches(1)
            top = Inches(1.5)
            width = Inches(8)
            height = Inches(1.5)
            
            title_box = slide.shapes.add_textbox(left, top, width, height)
            title_frame = title_box.text_frame
            title_frame.text = "AI Generated Presentation"
            
            if title_frame.paragraphs:
                paragraph = title_frame.paragraphs[0]
                paragraph.alignment = PP_ALIGN.CENTER
                font = paragraph.font
                font.size = Pt(44)
                font.bold = True
                
        except Exception as e:
            print(f"Error adding fallback title slide: {e}")
    
    def _add_fallback_content_slide(self, prs: Presentation, slide_data: Dict[str, Any], slide_number: int):
        """Add a basic content slide as fallback"""
        try:
            slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(slide_layout)
            
            # Add title text box
            left = Inches(1)
            top = Inches(0.5)
            width = Inches(8)
            height = Inches(1)
            
            title_box = slide.shapes.add_textbox(left, top, width, height)
            title_frame = title_box.text_frame
            title_frame.text = slide_data.get("title", f"Slide {slide_number}")
            
            if title_frame.paragraphs:
                paragraph = title_frame.paragraphs[0]
                font = paragraph.font
                font.size = Pt(36)
                font.bold = True
            
            # Add content text box
            content_top = Inches(2)
            content_height = Inches(5)
            
            content_box = slide.shapes.add_textbox(left, content_top, width, content_height)
            content_frame = content_box.text_frame
            content_frame.clear()
            
            bullet_points = slide_data.get("bullet_points", ["Content could not be generated"])
            for i, point in enumerate(bullet_points):
                if i == 0:
                    p = content_frame.paragraphs[0]
                else:
                    p = content_frame.add_paragraph()
                p.text = f"• {point}"
                font = p.font
                font.size = Pt(24)
                
        except Exception as e:
            print(f"Error adding fallback content slide: {e}")
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (64, 64, 64)  # Default dark gray
    
    def get_presentation_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about the generated presentation"""
        try:
            file_size = os.path.getsize(file_path)
            
            return {
                "file_path": file_path,
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "template_style": self.template_style,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "file_path": file_path,
                "error": str(e)
            }
