import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.shared.models.question import GeneratedQuestion
from src.shared.utils.pdf_generator import generate_question_pdf

def test_pdf_gen():
    print("Testing PDF Generation with Math...")
    
    q1 = GeneratedQuestion(
        subject="Physics",
        grade="11",
        medium="English",
        chapter_id="PH01",
        chapter_name="Kinematics",
        question_type="mcq",
        question_text="Calculate the kinetic energy of a 2kg object moving at 3m/s. Formula: $KE = \\frac{1}{2}mv^2$",
        options=json.dumps(["9 J", "18 J", "4.5 J", "6 J"]),
        answer=json.dumps(["9 J"]),
        explanation="Using $KE = 0.5 * 2 * 3^2$, we get $9$ Joules. This is a scalar quantity."
    )
    
    q2 = GeneratedQuestion(
        subject="Physics",
        grade="11",
        medium="English",
        chapter_id="PH01",
        chapter_name="Kinematics",
        question_type="structured",
        question_text="Derive the equation for velocity: $v = u + at$. Show all steps clearly.",
        options="[]",
        answer=json.dumps(["To derive $v = u + at$, we start with the definition of acceleration: $a = \\frac{dv}{dt}$. Rearranging gives $dv = a dt$. Integrating both sides from $t=0$ to $t=t$, we get $\\int_{u}^{v} dv = \\int_{0}^{t} a dt$. Performing the integration: $[v]_{u}^{v} = a[t]_{0}^{t}$, which simplifies to $v - u = at$. Therefore, $v = u + at$."]),
        explanation="This derivation assumes constant acceleration $a$. It is a fundamental kinematic equation."
    )
    
    questions = [q1, q2]
    
    try:
        pdf_buffer = generate_question_pdf(questions)
        with open("test_output.pdf", "wb") as f:
            f.write(pdf_buffer.getvalue())
        print("SUCCESS: PDF generated at 'test_output.pdf'. Please check manual rendering.")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_gen()
