import os
import hubspot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, ApiException
from hubspot.crm.objects.notes import SimplePublicObjectInputForCreate as NoteInput

def push_to_hubspot(name, email, company, score, category, reason, email_draft):
    """
    Creates a Contact in HubSpot and attaches a Note with the AI analysis.
    """
    token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    if not token or not token.startswith("pat-"):
        print("Warning: Valid HUBSPOT_ACCESS_TOKEN not set. Skipping CRM push.")
        return False
        
    client = hubspot.Client.create(access_token=token)
    
    # Split name into first and last
    parts = name.split(" ", 1)
    firstname = parts[0]
    lastname = parts[1] if len(parts) > 1 else ""
    
    # 1. Create the Contact
    properties = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "company": company,
        "lifecyclestage": "lead"
    }

    simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties=properties)
    
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
                print("Failed to parse existing contact ID: %s" % parse_e)
                return False
        else:
            print("Exception when communicating with HubSpot: %s\n" % e)
            return False
            
    try:
        # 2. Attach a Note with the AI Analysis & Email Draft
        note_body = (
            f"<b>AI Lead Analysis</b><br>"
            f"<b>Score:</b> {score}/100 ({category})<br>"
            f"<b>Reasoning:</b> {reason}<br><br>"
            f"<b>AI Drafted Email:</b><br>{email_draft.replace(chr(10), '<br>')}"
        )
        
        note_properties = {
            "hs_timestamp": "2024-01-01T00:00:00Z", # Placeholder, HubSpot overrides with current
            "hs_note_body": note_body
        }
        
        note_input = NoteInput(
            properties=note_properties, 
            associations=[
                {
                    "to": {"id": contact_id}, 
                    "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}] # 202 is Contact to Note
                }
            ]
        )
        
        client.crm.objects.notes.basic_api.create(simple_public_object_input_for_create=note_input)
        print("Successfully attached AI Analysis Note to Contact!")
        return True
        
    except ApiException as e:
        print("Exception when communicating with HubSpot: %s\n" % e)
        return False
