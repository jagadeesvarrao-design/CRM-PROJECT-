import requests
res = requests.post("http://127.0.0.1:5000/submit-lead", json={
    "name": "JAGADEES", 
    "email": "jagadeesvarrao@gmail.com", 
    "website_url": "https://www.nike.com", 
    "company": "NIKE", 
    "role": "CEO", 
    "company_size": "500+", 
    "message": "We need a new system"
})
print("STATUS CODE:", res.status_code)
print("RESPONSE:", res.text)
