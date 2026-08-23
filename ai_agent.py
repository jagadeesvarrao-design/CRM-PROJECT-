import os
import json
from google import genai
from google.genai import types

def analyze_inbound_inquiry(product, name, email, phone="", message="", rating=None, inquiry_type="general", company="", role=""):
    """
    Analyzes multi-product inbound leads/inquiries for Aneevarp Solutions (ZenResume & ZenScout AI).
    Categorizes the ticket, computes priority score (0-100), and drafts an official response.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are the Senior Operations & Customer Success Intelligence Engine for Aneevarp Solutions (MSME: UDYAM-AP-10-0144446),
    the software parent company operating:
    1. ZenResume (https://www.zenresume.online) - Free ATS Resume Builder & Career Hub
    2. ZenScout AI (https://ai-job-search-agent-chi.vercel.app) - Autonomous AI Job Search & Matching Agent

    Analyze the following inbound submission from our product ecosystem:

    Submission Details:
    - Product: {product if product else "Aneevarp Solutions (General)"}
    - Submitter Name: {name}
    - Submitter Email: {email}
    - Submitter Phone: {phone if phone else "Not provided"}
    - Declared Type: {inquiry_type}
    - User Rating/Score: {rating if rating is not None else "Not provided"}
    - Company / Institution: {company if company else "Not specified"}
    - Role: {role if role else "Not specified"}
    - Message / Inquiry: {message}

    Your Tasks:
    1. Categorize into EXACTLY ONE of these categories:
       - "B2B Enterprise Lead" (HR Tech, Corporate Hiring, SaaS integration, recruitment agencies)
       - "University Placement Partnership" (Colleges, universities, TPOs, student placement cells)
       - "Feature Suggestion" (Product ideas, UI/UX feedback, new feature requests)
       - "Customer Support" (Usage questions, account assistance, resume formatting/download questions, matching queries)
       - "Bug Report" (Errors, crashes, broken buttons, UI glitches, parsing issues)

    2. Priority Level: "Urgent" (Critical bugs or major B2B/College deals), "High" (Partnerships, serious bugs, high-intent enterprise), "Medium" (General support, helpful feature ideas), "Low" (Minor feedback/vague queries).

    3. Lead Score (0 to 100):
       - B2B Enterprise / University Placement: 75 - 100 (Higher if company/college specified with clear intent).
       - Bug Report: 60 - 90 (Higher if high severity).
       - Feature Suggestion / Customer Support: 40 - 75.
       - Vague / Spam: 0 - 30.

    4. Executive Summary (1-2 sentences): A crisp summary for the Founder & Operations Team.

    5. Personalized Drafted Response:
       - Written from the perspective of "Aneevarp Solutions Support Team" or the dedicated product team ("The ZenResume Team" or "The ZenScout AI Team").
       - Empathetic, highly professional, warm, addressing their specific message/problem directly.
       - Mention relevant product links (e.g. https://www.zenresume.online or https://ai-job-search-agent-chi.vercel.app).
       - Keep it concise, friendly, and actionable (under 120 words).
    """

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "category": {
                "type": "STRING",
                "description": "One of: B2B Enterprise Lead, University Placement Partnership, Feature Suggestion, Customer Support, Bug Report"
            },
            "priority": {
                "type": "STRING",
                "description": "Urgent, High, Medium, or Low"
            },
            "score": {
                "type": "INTEGER",
                "description": "Calculated score from 0 to 100"
            },
            "summary": {
                "type": "STRING",
                "description": "Short executive summary for the leadership team"
            },
            "email_draft": {
                "type": "STRING",
                "description": "Warm, branded customer response"
            },
            "action_items": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "1-3 recommended immediate action items for the operations team"
            }
        },
        "required": ["category", "priority", "score", "summary", "email_draft", "action_items"]
    }

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.2,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Gemini for inquiry analysis: {e}")
        return {
            "category": "Customer Support",
            "priority": "Medium",
            "score": 50,
            "summary": f"Inbound submission received for {product}: {message[:100]}",
            "email_draft": f"Dear {name},\n\nThank you for reaching out to us at Aneevarp Solutions regarding {product}. We have received your inquiry and our team is reviewing it. We will get back to you shortly.\n\nBest regards,\nThe {product} Team\nAneevarp Solutions",
            "action_items": ["Review inquiry manually in dashboard", "Follow up with user via email"]
        }
