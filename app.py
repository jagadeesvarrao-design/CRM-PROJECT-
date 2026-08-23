import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import customized Aneevarp Solutions modules
from ai_agent import analyze_inbound_inquiry
from crm_manager import push_to_hubspot
from notifier import send_email_alert, send_whatsapp_alert, send_customer_autoresponder

load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes (allows requests from zenresume.online, vercel, webflow, localhost, etc.)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def process_inbound_ticket(data):
    """
    Central Inbound Processing Engine for Aneevarp Solutions & Flagship Products:
    - ZenResume (https://www.zenresume.online)
    - ZenScout AI (https://ai-job-search-agent-chi.vercel.app)
    """
    product = data.get("product", "ZenResume")
    name = data.get("name", "Anonymous Submitter")
    email = data.get("email", "")
    phone = data.get("phone", "")
    inquiry_type = data.get("type", "general")
    rating = data.get("rating", None)
    company = data.get("company", "")
    role = data.get("role", "")
    message = data.get("message", "")

    print(f"\n--- [Aneevarp Hub] New Inbound Submission ---")
    log_text = f"Product: {product} | Name: {name} | Email: {email} | Type: {inquiry_type}"
    print(log_text.encode('ascii', 'replace').decode('ascii'))

    # 1. AI Analysis & Categorization via Gemini 2.5 Flash
    print(f"Analyzing submission for {product} with Gemini AI...")
    ai_result = analyze_inbound_inquiry(
        product=product,
        name=name,
        email=email,
        phone=phone,
        message=message,
        rating=rating,
        inquiry_type=inquiry_type,
        company=company,
        role=role
    )

    category = ai_result.get("category", "Customer Support")
    priority = ai_result.get("priority", "Medium")
    score = ai_result.get("score", 50)
    summary = ai_result.get("summary", "")
    email_draft = ai_result.get("email_draft", "")
    action_items = ai_result.get("action_items", [])

    print(f"Result: Category='{category}' | Priority='{priority}' | Score={score}/100")

    # 2. Push to HubSpot CRM
    crm_synced = False
    if email:
        print(f"Syncing contact to HubSpot CRM...")
        crm_synced = push_to_hubspot(
            name=name,
            email=email,
            phone=phone,
            product=product,
            category=category,
            priority=priority,
            score=score,
            summary=summary,
            email_draft=email_draft,
            user_message=message,
            rating=rating,
            company=company,
            role=role
        )

    # 3. Trigger Alerts for Operations Team & Founder
    print("Dispatching Operations Notifications...")
    # Email alert to central team
    send_email_alert(
        name=name,
        email=email,
        phone=phone,
        product=product,
        category=category,
        priority=priority,
        score=score,
        summary=summary,
        user_message=message,
        email_draft=email_draft
    )

    # WhatsApp alert to Founder
    send_whatsapp_alert(
        name=name,
        product=product,
        category=category,
        priority=priority,
        score=score,
        user_message=message,
        rating=rating,
        phone=phone,
        email=email
    )

    # 4. Dispatch Autoresponder to Submitter
    autoresponder_sent = False
    if email:
        print(f"Sending branded Aneevarp / {product} Autoresponder to {email}...")
        autoresponder_sent = send_customer_autoresponder(
            customer_name=name,
            customer_email=email,
            product=product,
            category=category,
            email_draft=email_draft
        )

    return {
        "success": True,
        "product": product,
        "category": category,
        "priority": priority,
        "score": score,
        "summary": summary,
        "action_items": action_items,
        "email_draft": email_draft,
        "crm_synced": crm_synced,
        "autoresponder_sent": autoresponder_sent
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/inbound-lead", methods=["POST", "OPTIONS"])
@app.route("/api/webhook", methods=["POST", "OPTIONS"])
@app.route("/submit-lead", methods=["POST", "OPTIONS"])
def inbound_lead_endpoint():
    """
    Main Multi-Product REST Endpoint for ZenResume & ZenScout AI.
    Accepts JSON payloads from client websites or external webhooks.
    """
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON body received"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name and not email and not message:
        return jsonify({"status": "error", "message": "Payload must contain at least name, email, or message."}), 400

    try:
        result = process_inbound_ticket(data)
        return jsonify({
            "status": "success",
            "message": f"Submission processed for {result['product']}! Categorized as {result['category']}.",
            **result
        }), 200
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        print(f"Error processing inbound ticket: {trace}")
        return jsonify({
            "status": "error",
            "message": f"Server processing error: {str(e)}"
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Aneevarp Solutions Inbound Hub",
        "enterprise": "Aneevarp Solutions (UDYAM-AP-10-0144446)",
        "products": [
            {"name": "ZenResume", "url": "https://www.zenresume.online"},
            {"name": "ZenScout AI", "url": "https://ai-job-search-agent-chi.vercel.app"}
        ]
    }), 200


@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    trace = traceback.format_exc()
    print(f"Unhandled Exception: {trace}")
    return jsonify({"status": "error", "message": f"Server Exception: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
