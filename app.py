from flask import Flask, render_template, request
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from hubspot_service import (
    get_contact,
    update_integration_link,
    get_all_contacts,
    update_company_integration_link,
    get_company,
    headers
)

from straits_service import (
    login_to_straits,
    create_employee
)

from organization_service import (
    login_user,
    register_user,
    create_organization
)

app = Flask(__name__)


# =====================================================
# HOME
# =====================================================

# @app.route("/")
# def home():

#     return {
#         "message":
#             "HubSpot-Straits Integration Running"
#     }

@app.route("/")
def home():

    contacts_data = get_all_contacts()

    contacts = contacts_data.get(
        "results",
        []
    )

    # AUTO UPDATE CONTACT LINKS

    for contact in contacts:

        contact_id = contact["id"]

        try:

            update_integration_link(
                contact_id
            )

        except Exception as e:

            print(
                "CONTACT LINK ERROR:",
                e
            )



# =====================================================
# COMPANY LINK SYNC
# =====================================================

@app.route("/sync-company-links")
def sync_company_links():

    url = (
        "https://api.hubapi.com/crm/v3/objects/companies"
    )

    response = requests.get(
        url,
        headers=headers
    )

    companies = response.json().get(
        "results",
        []
    )

    for company in companies:

        company_id = company["id"]

        try:

            update_company_integration_link(
                company_id
            )

        except Exception as e:

            print(
                "COMPANY LINK ERROR:",
                e
            )

    return {
        "message":
            "Company links synced"
    }



@app.route(
    "/hubspot-company-webhook",
    methods=["POST"]
)
def hubspot_company_webhook():

    data = request.json

    print("\n========== WEBHOOK ==========")

    print(data)

    for event in data:

        company_id = event.get(
            "objectId"
        )

        if company_id:

            try:

                update_company_integration_link(
                    company_id
                )

                print(
                    f"✅ LINK UPDATED: {company_id}"
                )

            except Exception as e:

                print(
                    "WEBHOOK ERROR:",
                    e
                )

    return {
        "message":
            "Webhook received"
    }



# =====================================================
# EMPLOYEE INTEGRATION
# =====================================================

@app.route(
    "/integrate/<contact_id>",
    methods=["GET", "POST"]
)
def integrate(contact_id):

    contact = get_contact(contact_id)

    properties = contact.get(
        "properties",
        {}
    )

    employee_data = {

        "full_name":
            f"{properties.get('firstname', '')} "
            f"{properties.get('lastname', '')}",

        "email":
            properties.get(
                "email",
                ""
            ),

        "role":
            properties.get(
                "employee_role",
                "INSPECTOR"
            ).upper(),

        "status":
            properties.get(
                "employee_status",
                "ACTIVE"
            ).upper()
    }

    if request.method == "POST":

        org_email = request.form.get(
            "org_email"
        )

        org_password = request.form.get(
            "org_password"
        )

        print("\n========== LOGIN ==========")

        login_response = login_to_straits(
            org_email,
            org_password
        )

        print(login_response)

        token = (
            login_response.get("data", {})
            .get("tokens", {})
            .get("access", {})
            .get("token")
        )

        if not token:

            return {
                "error":
                    "Login Failed",

                "response":
                    login_response
            }

        role_mapping = {

            "MANAGER":
                "MANAGER",

            "AUDITOR":
                "AUDITOR",

            "INSPECTOR":
                "INSPECTOR",

            "ORG_ADMIN":
                "ORG_ADMIN"
        }

        employee_payload = {

            "name":
                employee_data["full_name"],

            "email":
                employee_data["email"],

            "role":
                role_mapping.get(
                    employee_data["role"],
                    "INSPECTOR"
                ),

            "status":
                employee_data["status"]
        }

        print("\n========== EMPLOYEE ==========")

        print(employee_payload)

        create_response = create_employee(
            token,
            employee_payload
        )

        print(create_response)

        return create_response

    return render_template(
        "integrate.html",
        employee=employee_data
    )


# =====================================================
# ORGANIZATION INTEGRATION
# =====================================================

@app.route(
    "/company-preview/<company_id>",
    methods=["GET", "POST"]
)
def company_preview(company_id):

    company = get_company(company_id)

    properties = company.get(
        "properties",
        {}
    )

    organization_data = {

        "name":
            f"{properties.get('name')}_{company_id}",

        "type":
            properties.get(
                "organization_type",
                "startup"
            ).lower(),

        "description":
            properties.get(
                "organization_description",
                ""
            ),

        "employeesCount":
            properties.get(
                "employees_count",
                "1-10"
            )
    }

    smartarch_email = properties.get(
        "smartarch_email",
        ""
    )

    smartarch_password = properties.get(
        "smartarch_password",
        ""
    )

    if request.method == "POST":

        smartarch_email = request.form.get(
            "smartarch_email"
        )

        smartarch_password = request.form.get(
            "smartarch_password"
        )

        # =====================================
        # LOGIN TRY
        # =====================================

        print("\n========== LOGIN TRY ==========")

        login_response = login_user(
            smartarch_email,
            smartarch_password
        )

        print(login_response)

        token = (
            login_response.get("data", {})
            .get("tokens", {})
            .get("access", {})
            .get("token")
        )

        # =====================================
        # REGISTER IF LOGIN FAILS
        # =====================================

        if not token:

            print("\n========== REGISTER ==========")

            register_response = register_user(

                smartarch_email,

                smartarch_password,

                organization_data["name"]
            )

            print(register_response)

            # LOGIN AGAIN

            login_response = login_user(

                smartarch_email,

                smartarch_password
            )

            print(login_response)

            token = (
                login_response
                .get("data", {})
                .get("tokens", {})
                .get("access", {})
                .get("token")
            )

        # =====================================
        # LOGIN/REGISTER FAILED
        # =====================================

        if not token:

            return {

                "error":
                    "Unable to login/register",

                "response":
                    login_response
            }

        print("\n========== TOKEN ==========")

        print(token)

        # =====================================
        # CREATE ORGANIZATION
        # =====================================

        print("\n========== ORGANIZATION ==========")

        print(organization_data)

        create_response = create_organization(
            token,
            organization_data
        )

        print(create_response)

        return create_response

    return render_template(
        "organization_preview.html",
        organization=organization_data,
        email=smartarch_email
    )


# =====================================================
# AUTO CONTACT LINK SYNC
# =====================================================

def auto_sync_links():

    print("\n========== AUTO SYNC STARTED ==========")

    # CONTACTS

    contacts_data = get_all_contacts()

    contacts = contacts_data.get(
        "results",
        []
    )


    for contact in contacts:

        contact_id = contact["id"]

        properties = contact.get(
            "properties",
            {}
        )

        existing_link = properties.get(
            "integrate_with_straits"
        )

        # SKIP IF ALREADY EXISTS

        if existing_link:

            print(
                f"⏭️ Contact Already Synced: {contact_id}"
            )

            continue

        try:

            update_integration_link(
                contact_id
            )

            print(
                f"✅ Contact Link Updated: {contact_id}"
            )

        except Exception as e:

            print(
                "CONTACT SYNC ERROR:",
                e
            )



    # COMPANIES

    url = (
        "https://api.hubapi.com/crm/v3/objects/companies"
    )

    response = requests.get(
        url,
        headers=headers
    )

    companies = response.json().get(
        "results",
        []
    )


    for company in companies:

        company_id = company["id"]

        properties = company.get(
            "properties",
            {}
        )

        existing_link = properties.get(
            "integrate_with_straits"
        )

        # SKIP IF ALREADY EXISTS

        if existing_link:

            print(
                f"⏭️ Company Already Synced: {company_id}"
            )

            continue

        try:

            update_company_integration_link(
                company_id
            )

            print(
                f"✅ Company Link Updated: {company_id}"
            )

        except Exception as e:

            print(
                "COMPANY SYNC ERROR:",
                e
            )



    print(
        "✅ AUTO SYNC COMPLETED"
    )
# =====================================================
# MAIN
# =====================================================
scheduler = BackgroundScheduler()

scheduler.add_job(
    auto_sync_links,
    "interval",
    seconds=10
)

scheduler.start()

print("✅ Scheduler Started")

# FIRST RUN
auto_sync_links()


if __name__ == "__main__":

    app.run(debug=True)