import io
import json
import textwrap
from typing import List, Union
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Indenter, Image as RLImage, KeepTogether

# Matplotlib for Math Rendering
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt

from src.shared.models.question import GeneratedQuestion

def render_math_to_image(text: str, fontsize=12, max_width_char=80) -> Union[RLImage, None]:
    """
    Renders text containing LaTeX math ($...$) to a ReportLab Image using Matplotlib.
    Returns None if rendering fails.
    """
    try:
        # Wrap text for the image
        wrapped_lines = textwrap.wrap(text, width=max_width_char)
        wrapped_text = "\n".join(wrapped_lines)
        
        # Estimate height based on lines
        # This is a bit heuristic.
        lines_count = len(wrapped_lines)
        fig_height = lines_count * 0.3 + 0.5 # inches
        fig_width = 7.0 # inches (A4/Letter width minus margins approx)

        fig = plt.figure(figsize=(fig_width, fig_height))
        # Remove axes
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        
        # Render text with Math (Matplotlib handles $...$)
        # use raw string or escape backslashes? textwrap might mess up backslashes?
        # We assume the input text has proper LaTeX.
        
        # Place text at top-left
        ax.text(0.01, 0.9, wrapped_text, 
                fontsize=fontsize, 
                ha='left', 
                va='top', 
                wrap=True,
                family='serif' 
               )
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200, transparent=True)
        plt.close(fig)
        buf.seek(0)
        
        # Create ReportLab Image
        img = RLImage(buf)
        # Scale to fit width of PDF column (approx 6.5 inches)
        img.drawHeight = fig_height * 72 * 0.8 # Scale down a bit to match PDF pts
        img.drawWidth = fig_width * 72 * 0.8
        
        return img
    except Exception as e:
        print(f"Error rendering math: {e}")
        return None

def generate_question_pdf(questions: List[GeneratedQuestion]) -> io.BytesIO:
    """
    Generates a PDF file from a list of GeneratedQuestion objects.
    Correct answers are highlighted in RED.
    Renders fields with '$' as images for Math support.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    normal_style = styles["BodyText"]
    
    # Custom styles
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=10
    )
    
    option_style = ParagraphStyle(
        'Option',
        parent=styles['BodyText'],
        leftIndent=20,
        spaceAfter=5
    )
    
    correct_option_style = ParagraphStyle(
        'CorrectOption',
        parent=option_style,
        textColor=colors.red
    )
    
    explanation_style = ParagraphStyle(
        'Explanation',
        parent=styles['BodyText'],
        textColor=colors.blue,
        fontSize=10,
        leftIndent=10,
        spaceBefore=5
    )
    
    model_answer_style = ParagraphStyle(
        'ModelAnswer',
        parent=styles['BodyText'],
        textColor=colors.darkgreen,
        fontSize=11,
        leftIndent=20,
        spaceBefore=5,
        fontName='Helvetica-BoldOblique'
    )
    
    explanation_title_style = ParagraphStyle(
        'ExplanationTitle',
        parent=styles['BodyText'],
        textColor=colors.black,
        fontSize=10,
        leftIndent=10,
        spaceBefore=5,
        fontName='Helvetica-Bold'
    )

    story = []
    
    # Title
    story.append(Paragraph("Question Bank Export", title_style))
    story.append(Spacer(1, 20))
    
    for i, q in enumerate(questions, 1):
        q_story = [] # Group question elements to keep together if possible
        
        # --- Question Text ---
        display_text = q.question_text
        if q.question_type == "fill_in_the_blank":
             for placeholder in range(5):
                 display_text = display_text.replace(f"{{{placeholder}}}", "_______")

        if "$" in display_text:
            # Render as Image
            img = render_math_to_image(f"{i}. {display_text}", fontsize=12, max_width_char=75)
            if img:
                q_story.append(img)
            else:
                q_story.append(Paragraph(f"{i}. {display_text}", question_style))
        else:
            q_story.append(Paragraph(f"{i}. {display_text}", question_style))
        
        
        # --- Options ---
        try:
            options = json.loads(q.options)
        except:
            options = []
        try:
            answers = json.loads(q.answer)
            answer_set = set(answers)
        except:
            answers = []
            answer_set = set()

        if q.question_type == 'mcq':
            for opt in options:
                is_correct = opt in answer_set
                bullet = "\u2022"
                text_content = f"{bullet} {opt}"
                
                # Check for math in options
                if "$" in opt:
                    img = render_math_to_image(text_content, fontsize=10, max_width_char=80)
                    if img:
                        # Indent image? RLImage doesn't support leftIndent easily in Flowable list without Table or Indenter
                        # Use Indenter
                        q_story.append(Indenter(left=20))
                        q_story.append(img)
                        q_story.append(Indenter(left=-20))
                    else:
                         style = correct_option_style if is_correct else option_style
                         q_story.append(Paragraph(text_content, style))
                else:
                    style = correct_option_style if is_correct else option_style
                    q_story.append(Paragraph(text_content, style))
                
        elif q.question_type == 'fill_in_the_blank':
            if options:
                q_story.append(Paragraph("Word Bank:", normal_style))
                bank_text = ", ".join(options)
                q_story.append(Paragraph(bank_text, option_style))
            
            ans_text = ", ".join(answers)
            q_story.append(Paragraph(f"Answer: {ans_text}", correct_option_style))

        elif q.question_type == 'structured':
            # For structured questions, show the model answer clearly.
            q_story.append(Spacer(1, 10))
            
            # Show Answer if available
            if answers:
                # Structured answers can be long.
                ans_text = " ".join(answers) 
                
                q_story.append(Paragraph("Model Answer:", explanation_title_style))
                
                # Check for math in answer
                if "$" in ans_text:
                     img = render_math_to_image(ans_text, fontsize=11, max_width_char=80)
                     if img:
                        q_story.append(Indenter(left=20))
                        q_story.append(img)
                        q_story.append(Indenter(left=-20))
                     else:
                        q_story.append(Paragraph(ans_text, model_answer_style))
                else:
                    q_story.append(Paragraph(ans_text, model_answer_style))

        # --- Explanation ---
        if q.explanation:
            q_story.append(Spacer(1, 5))
            q_story.append(Paragraph("Explanation:", explanation_title_style))
            
            if "$" in q.explanation:
                img = render_math_to_image(q.explanation, fontsize=10, max_width_char=90)
                if img:
                    q_story.append(Indenter(left=10))
                    q_story.append(img)
                    q_story.append(Indenter(left=-10))
                else:
                    q_story.append(Paragraph(q.explanation, explanation_style))
            else:
                q_story.append(Paragraph(q.explanation, explanation_style))
            
        q_story.append(Spacer(1, 20))
        
        # Add group to story
        story.extend(q_story)
    
    doc.build(story)
    buffer.seek(0)
    return buffer
