import os
from dotenv import load_dotenv
load_dotenv()

from ai_agent import analyze_inbound_inquiry

def run_tests():
    print("==================================================")
    print("Testing Aneevarp Solutions AI Inbound Intelligence")
    print("==================================================")

    # Test 1: ZenResume University Placement Partnership
    print("\n--- Test 1: University Placement Partnership ---")
    test1 = analyze_inbound_inquiry(
        product="ZenResume",
        name="Dr. S. K. Sharma",
        email="placements@andhrauniversity.edu.in",
        phone="+91 9440123456",
        message="We are the Training & Placement Cell of Andhra University. We want to adopt ZenResume for 2,500 engineering students in our upcoming 2026 campus placement drive.",
        rating=5,
        inquiry_type="partnership",
        company="Andhra University",
        role="Head of Placements"
    )
    print(f"Category: {test1.get('category')}")
    print(f"Priority: {test1.get('priority')}")
    print(f"Score: {test1.get('score')}")
    print(f"Summary: {test1.get('summary')}")
    print(f"Draft:\n{test1.get('email_draft')}")

    # Test 2: ZenScout AI Bug Report
    print("\n--- Test 2: Bug Report for ZenScout AI ---")
    test2 = analyze_inbound_inquiry(
        product="ZenScout AI",
        name="Ananya Verma",
        email="ananya.v@gmail.com",
        phone="",
        message="Whenever I click on 'Apply Automatically to LinkedIn Jobs', the modal freezes and shows a 403 error on Chrome browser.",
        rating=2,
        inquiry_type="bug",
        company="",
        role="Job Seeker"
    )
    print(f"Category: {test2.get('category')}")
    print(f"Priority: {test2.get('priority')}")
    print(f"Score: {test2.get('score')}")
    print(f"Summary: {test2.get('summary')}")
    print(f"Draft:\n{test2.get('email_draft')}")

    print("\nAll AI categorization & auto-drafting tests completed successfully!")

if __name__ == "__main__":
    run_tests()
