import requests
import os 
import dotenv 

dotenv.load_dotenv()
TOKEN = os.getenv("HUBSPOT_TOKEN")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def get_contact(contact_id):

    url = (
        f"https://api.hubapi.com/crm/v3/objects/contacts/"
        f"{contact_id}"
        "?properties=firstname,lastname,email,employee_role,employee_status"
    )

    response = requests.get(url, headers=headers)

    return response.json()


def update_integration_link(contact_id):

    url = (
        f"https://api.hubapi.com/crm/v3/objects/contacts/"
        f"{contact_id}"
    )

    integration_link = (
        f"https://hubspot-straits.onrender.com/integrate/{contact_id}"
    )

    payload = {
        "properties": {
            "integrate_with_straits":
                integration_link
        }
    }

    response = requests.patch(
        url,
        headers=headers,
        json=payload
    )

    print(
        f"UPDATED LINK: {contact_id}"
    )

    return response.json()


def get_all_contacts():

    url = (
        "https://api.hubapi.com/crm/v3/objects/contacts"
    )

    response = requests.get(
        url,
        headers=headers
    )

    return response.json()

def get_company(company_id):

    url = (
        f"https://api.hubapi.com/crm/v3/objects/companies/"
        f"{company_id}"
        "?properties="
        "name,"
        "organization_description,"
        "organization_type,"
        "employees_count,"
        "smartarch_email,"
        "smartarch_password"
    )

    response = requests.get(
        url,
        headers=headers
    )

    return response.json()


def update_company_integration_link(company_id):

    url = (
        f"https://api.hubapi.com/crm/v3/objects/companies/"
        f"{company_id}"
    )

    integration_link = (
        f"https://hubspot-straits.onrender.com/company-preview/{company_id}"
    )

    payload = {
        "properties": {
            "integrate_with_straits": integration_link
        }
    }

    response = requests.patch(
        url,
        headers=headers,
        json=payload
    )

    print("✅ COMPANY INTEGRATION LINK UPDATED")

    return response.json()