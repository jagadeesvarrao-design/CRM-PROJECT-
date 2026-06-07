import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

def send_email_alert(name, company, score, category, email_draft):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD")
    recipient_email = os.getenv("CRM_TEAM_EMAIL")
    
    if not all([sender_email, sender_password, recipient_email]):
        print("Missing Email credentials in .env. Skipping Email alert.")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f"🚨 HOT LEAD ALERT: {name} from {company} (Score: {score})"

    body = f"""
    <h2>New High-Value Lead!</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Company:</strong> {company}</p>
    <p><strong>AI Score:</strong> {score}/100 ({category})</p>
    <hr>
    <h3>AI Drafted Reply:</h3>
    <pre style="font-family: sans-serif; background-color: #f4f4f4; padding: 10px;">{email_draft}</pre>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("Successfully sent Email alert!")
        return True
    except Exception as e:
        print(f"Failed to send Email alert: {e}")
        return False

def send_whatsapp_alert(name, company, score):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
    to_number = os.getenv("CRM_HEAD_WHATSAPP_NUMBER")
    
    if not all([account_sid, auth_token, from_number, to_number]):
        print("Missing Twilio credentials in .env. Skipping WhatsApp alert.")
        return False

    client = Client(account_sid, auth_token)
    
    # Twilio WhatsApp numbers must be prefixed with 'whatsapp:'
    if not from_number.startswith('whatsapp:'):
        from_number = f"whatsapp:{from_number}"
    if not to_number.startswith('whatsapp:'):
        to_number = f"whatsapp:{to_number}"

    message_body = f"🚨 *HOT LEAD ALERT* 🚨\n\n*Name:* {name}\n*Company:* {company}\n*AI Score:* {score}/100\n\nCheck HubSpot or your Email for the drafted reply!"

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

def send_customer_autoresponder(customer_name, customer_email, customer_company):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_APP_PASSWORD")
    
    if not all([sender_email, sender_password, customer_email]):
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = customer_email
    msg['Subject'] = f"We've received your request, {customer_name}!"

    body = f"""
    <div style="font-family: sans-serif; color: #333; line-height: 1.6;">
        <p>Hi {customer_name},</p>
        <p>Thank you for reaching out! We have successfully received your inquiry regarding <strong>{customer_company}</strong>.</p>
        <p>Our executive team has been notified and is reviewing your request right now. One of our specialists will be in touch with you shortly.</p>
        <p>Best regards,<br><strong>The Sales Team</strong></p>
    </div>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Successfully sent autoresponder to {customer_email}")
        return True
    except Exception as e:
        print(f"Failed to send autoresponder: {e}")
        return False
