import requests

BASE_URL = "https://api-demo.straits.io/api"


def login_to_straits(email, password):

    payload = {
        "email": email,
        "password": password
    }

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=payload
    )

    return response.json()


def create_employee(token, employee_data):

    response = requests.post(
        f"{BASE_URL}/user/invite?changePasswordRequired=true",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=employee_data
    )

    return response.json()