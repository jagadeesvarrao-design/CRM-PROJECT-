import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

def send_email_alert(name, email, phone, product, category, priority, score, summary, user_message, email_draft):
    """
    Sends an executive alert email to the central operations team (aneevarpsolutions@gmail.com).
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD")
    recipient_email = os.getenv("CRM_TEAM_EMAIL", "aneevarpsolutions@gmail.com")
    
    if not all([sender_email, sender_password, recipient_email]):
        print("Missing Email credentials in .env. Skipping Operations Email alert.")
        return False

    product_label = product if product else "Aneevarp General"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"[{product_label}] {category} ({priority}) - {name} [Score: {score}]"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 20px; }}
            .card {{ background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; max-width: 650px; margin: auto; padding: 28px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
            .header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 16px; margin-bottom: 20px; }}
            .badge {{ display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
            .badge-urgent {{ background: #fee2e2; color: #b91c1c; }}
            .badge-high {{ background: #ffedd5; color: #c2410c; }}
            .badge-medium {{ background: #fef3c7; color: #b45309; }}
            .badge-low {{ background: #e0f2fe; color: #0369a1; }}
            .info-table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
            .info-table td {{ padding: 8px 0; border-bottom: 1px solid #f1f5f9; }}
            .info-label {{ font-weight: 600; color: #64748b; width: 35%; }}
            .info-value {{ color: #0f172a; font-weight: 500; }}
            .section-title {{ font-size: 14px; font-weight: bold; text-transform: uppercase; color: #475569; margin-top: 24px; }}
            .draft-box {{ background: #f1f5f9; border-left: 4px solid #3b82f6; padding: 14px; border-radius: 4px; font-size: 14px; white-space: pre-wrap; line-height: 1.5; }}
            .footer {{ font-size: 11px; color: #94a3b8; margin-top: 24px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <h2 style="margin:0; color:#0f172a;">Aneevarp Solutions Operations Hub</h2>
                <p style="margin:4px 0 0; color:#64748b; font-size:14px;">Inbound Lead & Ticket Processing Engine</p>
            </div>

            <div>
                <span class="badge badge-{priority.lower()}">{priority} Priority</span>
                <span style="font-size:13px; font-weight:600; margin-left:8px; color:#3b82f6;">Product: {product_label}</span>
                <span style="font-size:13px; font-weight:600; margin-left:8px; color:#10b981;">Score: {score}/100</span>
            </div>

            <table class="info-table">
                <tr><td class="info-label">Category</td><td class="info-value">{category}</td></tr>
                <tr><td class="info-label">Full Name</td><td class="info-value">{name}</td></tr>
                <tr><td class="info-label">Email</td><td class="info-value"><a href="mailto:{email}">{email}</a></td></tr>
                <tr><td class="info-label">Phone</td><td class="info-value">{phone if phone else "Not provided"}</td></tr>
            </table>

            <div class="section-title">Submitter Message</div>
            <p style="background:#f8fafc; border:1px solid #e2e8f0; padding:12px; border-radius:8px; font-size:14px; margin-top:6px;">{user_message}</p>

            <div class="section-title">AI Executive Summary</div>
            <p style="font-size:14px; color:#334155; margin-top:6px;">{summary}</p>

            <div class="section-title">Suggested Auto-Drafted Response</div>
            <div class="draft-box">{email_draft}</div>

            <div class="footer">
                Aneevarp Solutions (MSME: UDYAM-AP-10-0144446) • Operating ZenResume & ZenScout AI
            </div>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Successfully sent Operations Email alert to {recipient_email}!")
        return True
    except Exception as e:
        print(f"Failed to send Email alert: {e}")
        return False


def send_whatsapp_alert(name, product, category, priority, score, user_message, rating=None, phone="", email=""):
    """
    Sends structured Twilio WhatsApp alert to Founder / Operations Lead.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    to_number = os.getenv("CRM_HEAD_WHATSAPP_NUMBER")
    
    if not all([account_sid, auth_token, from_number, to_number]):
        print("Missing Twilio credentials in .env. Skipping WhatsApp alert.")
        return False

    client = Client(account_sid, auth_token)
    
    if not from_number.startswith('whatsapp:'):
        from_number = f"whatsapp:{from_number}"
    if not to_number.startswith('whatsapp:'):
        to_number = f"whatsapp:{to_number}"

    product_name = product if product else "Aneevarp Solutions"
    rating_display = f" | Rating: {rating}/5" if rating is not None else ""
    phone_display = f"\n*Phone:* {phone}" if phone else ""
    email_display = f"\n*Email:* {email}" if email else ""

    message_body = (
        f"🏢 *ANEEVARP SOLUTIONS - INBOUND HUB*\n\n"
        f"*Product:* {product_name}\n"
        f"*Category:* {category} [{priority}]\n"
        f"*Score:* {score}/100{rating_display}\n"
        f"*Submitter:* {name}{email_display}{phone_display}\n\n"
        f"*Message:*\n\"{user_message[:280]}\"\n\n"
        f"Logged to HubSpot & Central Hub."
    )

    try:
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        print(f"Successfully sent WhatsApp alert! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send WhatsApp alert: {e}")
        return False


def send_customer_autoresponder(customer_name, customer_email, product, category, email_draft=""):
    """
    Sends an automated, branded response to the customer from Aneevarp Solutions / ZenResume / ZenScout AI.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD")
    
    if not all([sender_email, sender_password, customer_email]):
        return False

    product_name = product if product else "Aneevarp Solutions"
    product_url = "https://www.zenresume.online" if "zenresume" in product_name.lower() else "https://ai-job-search-agent-chi.vercel.app"

    msg = MIMEMultipart()
    msg['From'] = f"Aneevarp Solutions Support <{sender_email}>"
    msg['To'] = customer_email
    msg['Subject'] = f"Thank you for reaching out to {product_name}"

    # Use AI drafted email if available, otherwise high quality template
    if email_draft:
        formatted_content = email_draft.replace("\n", "<br>")
    else:
        formatted_content = f"""
        Dear {customer_name},<br><br>
        Thank you for contacting the <strong>{product_name}</strong> team at <strong>Aneevarp Solutions</strong>.<br><br>
        We have received your inquiry regarding <strong>{category}</strong> and our team is actively reviewing your request. 
        We strive to address all inquiries promptly.<br><br>
        In the meantime, feel free to explore our platform at <a href="{product_url}">{product_url}</a>.<br><br>
        Warm regards,<br>
        <strong>The {product_name} Support & Operations Team</strong><br>
        Aneevarp Solutions (MSME: UDYAM-AP-10-0144446)
        """

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; color: #2d3748; line-height: 1.6; background-color: #f7fafc; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; padding: 24px;">
            <div style="border-bottom: 2px solid #4299e1; padding-bottom: 12px; margin-bottom: 16px;">
                <h3 style="margin: 0; color: #1a202c;">{product_name}</h3>
                <span style="font-size: 12px; color: #718096;">An enterprise product by Aneevarp Solutions</span>
            </div>
            <div style="font-size: 14px; color: #2d3748;">
                {formatted_content}
            </div>
            <hr style="border: none; border-top: 1px solid #edf2f7; margin: 24px 0 12px;">
            <div style="font-size: 11px; color: #a0aec0; text-align: center;">
                Aneevarp Solutions • Operating <a href="https://www.zenresume.online" style="color: #4299e1;">ZenResume</a> &amp; <a href="https://ai-job-search-agent-chi.vercel.app" style="color: #4299e1;">ZenScout AI</a>
            </div>
        </div>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Successfully sent customer autoresponder to {customer_email}")
        return True
    except Exception as e:
        print(f"Failed to send autoresponder to customer: {e}")
        return False
