import os
import hubspot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, ApiException
from hubspot.crm.objects.notes import SimplePublicObjectInputForCreate as NoteInput

def push_to_hubspot(name, email, phone="", product="Aneevarp Solutions", category="Customer Support", priority="Medium", score=50, summary="", email_draft="", user_message="", rating=None, company="", role=""):
    """
    Creates/Updates a Contact in HubSpot and attaches a rich Note with the Aneevarp Solutions AI analysis.
    """
    token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    if not token or not token.startswith("pat-"):
        print("Warning: Valid HUBSPOT_ACCESS_TOKEN not set. Skipping CRM push.")
        return False
        
    client = hubspot.Client.create(access_token=token)
    
    # Split name into first and last
    parts = name.strip().split(" ", 1)
    firstname = parts[0]
    lastname = parts[1] if len(parts) > 1 else ""
    
    # 1. Create the Contact
    company_val = company if company else f"{product} User"
    properties = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "company": company_val,
        "lifecyclestage": "lead" if "B2B" in category or "Partnership" in category else "customer"
    }

    if phone:
        properties["phone"] = phone
    if role:
        properties["jobtitle"] = role

    simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties=properties)
    
    contact_id = None
    try:
        api_response = client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=simple_public_object_input_for_create
        )
        contact_id = api_response.id
        print(f"Successfully created HubSpot Contact! ID: {contact_id}")
    except ApiException as e:
        if getattr(e, 'status', None) == 409:
            import json
            try:
                error_body = json.loads(e.body)
                msg = error_body.get('message', '')
                if 'Existing ID:' in msg:
                    contact_id = msg.split('Existing ID: ')[-1].split()[0].replace('"', '').replace(',', '').strip()
                    print(f"Contact already exists in HubSpot! Reusing Existing ID: {contact_id}")
                else:
                    print("Conflict error but no Existing ID found.")
                    return False
            except Exception as parse_e:
                print(f"Failed to parse existing contact ID: {parse_e}")
                return False
        else:
            print(f"Exception when communicating with HubSpot: {e}")
            return False
            
    if not contact_id:
        return False

    try:
        # 2. Attach a Rich Note with the AI Analysis & Drafted Reply
        rating_line = f"<b>User Rating:</b> {rating}/5<br>" if rating is not None else ""
        phone_line = f"<b>Phone:</b> {phone}<br>" if phone else ""
        
        note_body = (
            f"<h3>🏢 Aneevarp Solutions - {product} Inbound Ticket</h3>"
            f"<b>Category:</b> {category} (Priority: {priority})<br>"
            f"<b>AI Score:</b> {score}/100<br>"
            f"{rating_line}"
            f"{phone_line}"
            f"<b>Executive Summary:</b> {summary}<br>"
            f"<hr>"
            f"<b>Original Message:</b><br>{user_message.replace(chr(10), '<br>')}<br>"
            f"<hr>"
            f"<b>AI Suggested Response:</b><br>{email_draft.replace(chr(10), '<br>')}"
        )
        
        note_properties = {
            "hs_timestamp": "2026-08-23T00:00:00Z",
            "hs_note_body": note_body
        }
        
        note_input = NoteInput(
            properties=note_properties, 
            associations=[
                {
                    "to": {"id": contact_id}, 
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}]
                }
            ]
        )
        
        client.crm.objects.notes.basic_api.create(simple_public_object_input_for_create=note_input)
        print("Successfully attached AI Inbound Note to Contact in HubSpot!")
        return True
        
    except ApiException as e:
        print(f"Exception when attaching Note to HubSpot Contact: {e}")
        return False
