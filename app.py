import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Import our custom modules
from ai_agent import analyze_lead
from crm_manager import push_to_hubspot
from notifier import send_email_alert, send_whatsapp_alert, send_customer_autoresponder
from scraper import scrape_website

load_dotenv()

app = Flask(__name__)

# Basic Domain Validation (to filter out fake consumer leads)
PUBLIC_DOMAINS = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com']

def is_b2b_email(email):
    """Returns False if the email uses a public domain provider, True otherwise."""
    domain = email.split('@')[-1].lower()
    return domain not in PUBLIC_DOMAINS

def process_lead_data(data):
    """
    Core engine logic separated from Flask routing.
    This can be called by the web form or by a headless webhook.
    """
    name = data.get("name")
    email = data.get("email", "")
    website_url = data.get("website_url", "")
    company = data.get("company")
    role = data.get("role")
    company_size = data.get("company_size")
    message = data.get("message")
    
    print(f"\n--- New Lead Received ---")
    log_text = f"Name: {name} | Email: {email} | Company: {company} | Website: {website_url}"
    print(log_text.encode('ascii', 'replace').decode('ascii'))
    
    # 1. Email Domain Validation Check
    if email and not is_b2b_email(email):
        print("WARNING: Lead submitted with a public/free email domain (Fake entry risk).")
        # For testing, we just print a warning. In production, we could outright reject it:
        # return False, 0, "Rejected", "Public email domain rejected.", ""

    # 2. Web Scraping for Hyper-Personalization
    scraped_data = ""
    if website_url:
        print(f"Scraping website: {website_url}...")
        scraped_data = scrape_website(website_url)

    # 3. Analyze with Gemini
    print("AI is analyzing the lead...")
    analysis = analyze_lead(name, email, company, role, company_size, message, scraped_data)
    
    is_fake_identity = analysis.get("is_fake_identity", False)
    rejection_message = analysis.get("rejection_message", "")
    
    if is_fake_identity:
        print(f"FRAUD DETECTED: {rejection_message}")
        return False, 0, "Rejected", rejection_message, ""
    
    score = analysis.get("score", 0)
    category = analysis.get("category", "Error")
    reason = analysis.get("reason", "")
    email_draft = analysis.get("email_draft", "")
    
    print(f"Result: {score}/100 [{category}]")
    
    # 4. Push to HubSpot
    print("Pushing to HubSpot CRM...")
    success = push_to_hubspot(name, email, company, score, category, reason, email_draft)
    
    if success:
        # Trigger Alerts if Lead Score is 70 or above
        if score >= 70:
            print("HIGH-VALUE LEAD DETECTED! Triggering Alerts...")
            send_email_alert(name, company, score, category, email_draft)
            send_whatsapp_alert(name, company, score)

            print(f"Sending Auto-Responder to {email}...")
            send_customer_autoresponder(name, email, company)

    return success, score, category, reason, email_draft

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit-lead", methods=["POST"])
def submit_lead():
    data = request.json
    try:
        success, score, category, reason, email_draft = process_lead_data(data)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Lead processed! Score: {score} ({category}). Added to HubSpot.",
                "score": score,
                "category": category
            })
        else:
            if category == "Rejected":
                return jsonify({
                    "status": "error",
                    "message": reason
                }), 400
            return jsonify({
                "status": "error",
                "message": "Failed to process lead or push to CRM."
            }), 500
    except Exception as e:
        import traceback
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        return jsonify({"status": "error", "message": "Server crash: check crash.log"}), 500

@app.route("/api/webhook", methods=["POST"])
def webhook():
    """
    Enterprise Webhook endpoint. 
    Third-party services (Zapier, Webflow, Custom Sites) can POST JSON here.
    """
    data = request.json
    
    # In a real enterprise app, we would check an API Key here for security
    # api_key = request.headers.get("Authorization")
    # if api_key != f"Bearer SECRET_KEY": return jsonify({"error": "Unauthorized"}), 401
        
    success, score, category, reason, email_draft = process_lead_data(data)
    
    if success:
        return jsonify({"success": True, "lead_score": score, "status": "Processed"}), 200
    else:
        return jsonify({"success": False, "error": "Processing failed"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Return JSON instead of HTML for HTTP errors
    import traceback
    with open("crash.log", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    return jsonify({"status": "error", "message": f"Server Exception: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
