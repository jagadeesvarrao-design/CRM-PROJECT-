import os
import json
from google import genai
from google.genai import types

def analyze_lead(name, email, company, role, company_size, message, scraped_data=""):
    """
    Passes the lead data to Gemini to get a lead score and an email draft.
    Returns a dictionary with the results.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert B2B Sales Operations Analyst.
    Analyze the following inbound lead using the scoring rubric below.
    
    Here is the data we scraped from their company website:
    <website_data>
    {scraped_data}
    </website_data>

    Use this scraped website data to write an incredibly hyper-personalized outreach email. Reference specific things they do or sell based on the website data so it proves we actually researched them!
    
    Lead Details:
    - Name: {name}
    - Email: {email}
    - Company: {company}
    - Role/Job Title: {role}
    - Company Size: {company_size}
    - Pain Point / Message: {message}
    
    Identity Verification Rules:
    If the email is a public email (e.g. gmail.com, yahoo.com):
    - If they claim a low-level role (e.g., Manager, Employee, Student), set "is_fake_identity" to true, and set "rejection_message" to "Please use your official company email ID."
    - If they claim a high-level role (e.g., CEO, MD, Founder), check the scraped website data. If the website data explicitly lists someone else as the CEO/MD or if their name clearly doesn't match the actual leadership listed, set "is_fake_identity" to true and set "rejection_message" to "dont fake your idententity sir". If the website data is missing leadership names, give them the benefit of the doubt and set "is_fake_identity" to false.
    - If it's a valid B2B email, set "is_fake_identity" to false.

    Scoring Rubric (100 points total):
    1. Role/Decision Maker (20 pts): C-level, VP, or Director gets 20. Managers get 10. Others get 0.
    2. Company Size (20 pts): 500+ gets 20. 201-500 gets 15. 51-200 gets 10. 1-50 gets 0.
    3. Pain Point Clarity (20 pts): Clear, specific business problem gets 20. Vague gets 10. Blank/irrelevant gets 0.
    4. Budget/Timeline (20 pts): Mention of urgency (e.g., Q3, ASAP) gets 20. General interest gets 0.
    5. Overall Fit (20 pts): Does this sound like a real, high-value B2B lead? Yes=20, No=0.
    
    Task:
    1. Verify their identity based on the rules above.
    2. Calculate the final score (0 to 100).
    3. Categorize the lead: "Hot" (80-100), "Warm" (50-79), or "Cold" (Below 50).
    4. Provide a 1-sentence reason for this score.
    5. Draft a highly personalized introductory email (under 100 words) from our sales team to this lead, mentioning their specific pain point. DO NOT use generic placeholders like [Your Name]. Use "The Sales Team" instead.
    """

    # Define the expected JSON structure
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "score": {"type": "INTEGER", "description": "The calculated lead score (0-100)"},
            "category": {"type": "STRING", "description": "Hot, Warm, or Cold"},
            "reason": {"type": "STRING", "description": "1-sentence reason for the score"},
            "email_draft": {"type": "STRING", "description": "The personalized email draft"},
            "is_fake_identity": {"type": "BOOLEAN", "description": "True if the lead is faking their identity based on the rules."},
            "rejection_message": {"type": "STRING", "description": "The custom rejection message if is_fake_identity is true."}
        },
        "required": ["score", "category", "reason", "email_draft", "is_fake_identity", "rejection_message"]
    }

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.2, # Low temperature for more consistent scoring
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return {
            "score": 0,
            "category": "Error",
            "reason": str(e),
            "email_draft": "Could not generate email due to an error.",
            "is_fake_identity": False,
            "rejection_message": ""
        }
