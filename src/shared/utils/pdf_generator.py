import io
import json
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Indenter
from src.shared.models.question import GeneratedQuestion

def generate_question_pdf(questions: List[GeneratedQuestion]) -> io.BytesIO:
    """
    Generates a PDF file from a list of GeneratedQuestion objects.
    Correct answers are highlighted in RED.
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
        fontSize=9,
        leftIndent=10,
        spaceBefore=5
    )

    story = []
    
    # Title
    story.append(Paragraph("Question Bank Export", title_style))
    story.append(Spacer(1, 20))
    
    for i, q in enumerate(questions, 1):
        # Question Text
        # For fill in the blank, we might want to show formatted text, but raw text is okay for now.
        # If it has placeholders {0}, {1}, we leave them or replace with lines.
        # Let's replace {n} with _________ for the question text display?
        # The user said "filling the blank like filling the blank".
        
        display_text = q.question_text
        if q.question_type == "fill_in_the_blank":
             # Simple replacement for visual representation
             for placeholder in range(5):
                 display_text = display_text.replace(f"{{{placeholder}}}", "_______")

        story.append(Paragraph(f"{i}. {display_text}", question_style))
        
        # Parse options and answers
        try:
            options = json.loads(q.options)
        except:
            options = []
            
        try:
            # Answer is stored as a JSON list string "['A']" or "['answer']"
            answers = json.loads(q.answer)
            # Normalize to set for checking
            answer_set = set(answers)
        except:
            answers = []
            answer_set = set()

        # Display Options
        if q.question_type == 'mcq':
            for opt in options:
                # Check if this option is the answer
                # Note: Answer might be the text itself or index. 
                # The prompt says: "answer is a list containing the single correct option text."
                is_correct = opt in answer_set
                
                style = correct_option_style if is_correct else option_style
                bullet = "\u2022" # Bullet point
                
                story.append(Paragraph(f"{bullet} {opt}", style))
                
        elif q.question_type == 'fill_in_the_blank':
            # Show options bank if available, typically fill in blank might have a word bank
            if options:
                story.append(Paragraph("Word Bank:", normal_style))
                # For fill in blank, we just list them.
                # Highlight the correct words (which are in the answer list) in the bank?
                # Or just list the answer below?
                # User request: "mention the correct answer in red"
                
                # Let's list options normally
                bank_text = ", ".join(options)
                story.append(Paragraph(bank_text, option_style))
            
            # Show Answer Key for blank
            # Since blanks need to be filled, we show the answers clearly.
            ans_text = ", ".join(answers)
            story.append(Paragraph(f"Answer: {ans_text}", correct_option_style))

        # Explanation
        if q.explanation:
            story.append(Spacer(1, 5))
            story.append(Paragraph(f"<b>Explanation:</b> {q.explanation}", explanation_style))
            
        story.append(Spacer(1, 20))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
