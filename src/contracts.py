"""
Step 1: Create CLM contracts from a CSV file.

Reads rows from a Snowflake/HubSpot CSV export and creates a CLM contract
record in Onit for each row. Before creating, it looks up the Other Party
Contact ID by email (the contact must already exist in Onit).

Required CSV columns:
    COMPANY_NAME      - Company name (used for multiple party fields)
    CONTACT_NAME      - Full name of the contact
    CONTACT_EMAIL     - Email to look up the Other Party Contact record
    DEAL_ID           - HubSpot deal ID
    REQUESTING_EMAIL  - Email of the Onit user making the request

The contract is created with 9 fields:
    p_contract_type            = "Order Form" (always)
    p_deal_id                  = DEAL_ID from CSV
    p_custom_company_name      = COMPANY_NAME (displayed as "Company Name" in UI)
    p_other_party_name         = COMPANY_NAME
    p_other_party_select       = COMPANY_NAME (required for validation)
    p_other_party_select_contact = contact record ID (from lookup)
    p_other_party_contact_name   = CONTACT_NAME
    p_other_party_contact_email  = CONTACT_EMAIL
    requester_email              = REQUESTING_EMAIL (must be a real Onit user)
"""

import csv

from src.api import api_request
from src.config import CLM_DICTIONARY_ID
from src.lookups import lookup_contact_id


def create_contract(csv_path: str):
    """Read CSV and create a CLM contract for each row.

    For each row: looks up the contact by email, then POSTs to the
    CLM dictionary. Prints the new atom ID and the next command to run.
    Skips rows where the contact is not found.
    """
    contact_cache = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_name = row["COMPANY_NAME"].strip()
            contact_name = row["CONTACT_NAME"].strip()
            contact_email = row["CONTACT_EMAIL"].strip()
            deal_id = row["DEAL_ID"].strip()
            requester_email = row["REQUESTING_EMAIL"].strip()

            print(f"\n{'='*60}")
            print(f"  {company_name}  |  Deal {deal_id}")
            print(f"{'='*60}")

            print(f"\n  [1/2] Looking up contact: {contact_email}")
            if contact_email in contact_cache:
                contact_id = contact_cache[contact_email]
            else:
                contact_id = lookup_contact_id(contact_email)
                contact_cache[contact_email] = contact_id
            if not contact_id:
                print(f"  SKIP — no contact found for {contact_email}")
                continue
            print(f"        Found: {contact_id}")

            print(f"  [2/2] Creating contract...")
            result = api_request(
                "POST",
                f"/api/atom_dictionaries/{CLM_DICTIONARY_ID}/atoms",
                body={"atom": {
                    "p_contract_type": "Order Form",
                    "p_deal_id": deal_id,
                    "p_custom_company_name": company_name,
                    "p_other_party_name": company_name,
                    "p_other_party_select": company_name,
                    "p_other_party_select_contact": contact_id,
                    "p_other_party_contact_name": contact_name,
                    "p_other_party_contact_email": contact_email,
                    "requester_email": requester_email,
                }},
            )

            if result.get("success"):
                atom_id = result.get("data", "")
                print(f"        Created: {atom_id}")
                print(f"        Next:    python onit_client.py start-axdraft {atom_id}")
            else:
                print(f"        FAILED: {result.get('message')}")
