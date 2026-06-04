import requests

BASE_URL = "https://api-demo.straits.io/api"


def login_user(email, password):

    url = f"{BASE_URL}/auth/login"

    payload = {
        "email": email,
        "password": password
    }

    response = requests.post(
        url,
        json=payload
    )

    return response.json()


def register_user(email, password, name):

    url = f"{BASE_URL}/auth/register"

    payload = {
        "email": email,
        "password": password,
        "confirmPassword": password,
        "name": name
    }

    response = requests.post(
        url,
        json=payload
    )

    return response.json()


def create_organization(
    token,
    organization_data
):

    url = f"{BASE_URL}/organization"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        headers=headers,
        json=organization_data
    )

    return response.json()