"""
Step 2: Generate the Order Form document via the AxDraft API.

Instead of manually filling in the AxDraft questionnaire, this calls the
AxDraft process-draft API with pre-filled answers built from the CSV data.

The AxDraft API expects an array of {question, answer} pairs where:
  - "question" is the AxDraft variable name (Column B from the field mapping spreadsheet)
  - "answer" is the selected value

Questionnaire flow (confirmed from AxDraft UI):
  1. Generate a new order form  (hardcoded)
  2. What is the complexity?     Standard (hardcoded)
  3. What is the deal type?      from CSV PARTNER_TYPE
  4. Do you want to add W9?      Yes (hardcoded)
  5. Are you including a trial?  from CSV AXDRAFT_TRIAL_SELECTION
  6. Input fields page           Order ID, expiration, company info, contact, pricing

Field mapping reference:
  data/AXD Filters list - Consumer Direct API Integration.xlsx

API reference:
  docs/Generation API Integration - AXDRAFT.docx
"""

import csv
import json
import urllib.request
import urllib.error

from src.config import AXDRAFT_BASE_URL, AXDRAFT_TOKEN, AXDRAFT_DOCUMENT_ID


def build_answers(row: dict) -> list:
    """Build the AxDraft answers array from a CSV row.

    Maps CSV columns to AxDraft questionnaire variables using the field
    mapping from the AXD Filters spreadsheet.

    Args:
        row: A dict from csv.DictReader with the CSV columns.

    Returns:
        List of {"question": ..., "answer": ...} dicts.
    """
    company_name = row["COMPANY_NAME"].strip()
    contact_parts = row["CONTACT_NAME"].strip().split(" ", 1)
    first_name = contact_parts[0]
    last_name = contact_parts[1] if len(contact_parts) > 1 else ""
    contact_email = row["CONTACT_EMAIL"].strip()
    deal_id = row["DEAL_ID"].strip()
    partner_type = row["PARTNER_TYPE"].strip()
    build_price = row["RETAIL_PRICING_FOR_BUILD_PLAN"].strip()
    protect_price = row["RETAIL_PRICING_FOR_PROTECT_PLAN"].strip()
    trial_selection = row["AXDRAFT_TRIAL_SELECTION"].strip()
    expiration_date = row["EXPIRATION_DATE"].strip()

    # Format expiration date to MM/DD/YYYY if it's in M/D/YYYY
    if expiration_date:
        parts = expiration_date.split("/")
        if len(parts) == 3:
            expiration_date = f"{int(parts[0]):02d}/{int(parts[1]):02d}/{parts[2]}"

    answers = []

    # --- Selection Questions (5) ---

    # 1. New order form (hardcoded)
    answers.append({
        "question": "select_Do_you_want_to_generate_a_new_order_form_or_change_an_executed_order?",
        "answer": "Generate a new order form",
    })

    # 2. Deal complexity (hardcoded)
    answers.append({
        "question": "select_What_is_the_complexity_of_deal?",
        "answer": "Standard",
    })

    # 3. Deal type from CSV PARTNER_TYPE
    answers.append({
        "question": "select_What_is_the_deal_type?",
        "answer": partner_type,
    })

    # 4. W9 form (hardcoded)
    answers.append({
        "question": "select_Do_you_want_to_add_W9_form?",
        "answer": "Yes",
    })

    # 5. Trial period from CSV AXDRAFT_TRIAL_SELECTION
    answers.append({
        "question": "select_Are_you_including_a_trial_period?",
        "answer": trial_selection,
    })

    # --- Input Fields (12) ---

    # Order ID
    answers.append({
        "question": "Type_in_Order_ID",
        "answer": deal_id,
    })

    # Expiration date
    answers.append({
        "question": "Type_in_Expiration_date~d~dfr~MM/DD/YYYY",
        "answer": expiration_date,
    })

    # Company info
    answers.append({
        "question": "Type_in_Company_name~l",
        "answer": company_name,
    })
    # TODO: address fields hardcoded for now — may be auto-filled or added to CSV later
    answers.append({
        "question": "Type_in_Company_address~l",
        "answer": "44 Eagle Point",
    })
    answers.append({
        "question": "Type_in_Company_city~l",
        "answer": "Irvine",
    })
    answers.append({
        "question": "Type_in_Company_state_territory~l",
        "answer": "California",
    })
    answers.append({
        "question": "Type_in_Company_ZIP~l",
        "answer": "92604",
    })

    # Contact info
    answers.append({
        "question": "Type_in_Contact_firstname",
        "answer": first_name,
    })
    answers.append({
        "question": "Type_in_Contact_lastname",
        "answer": last_name,
    })
    answers.append({
        "question": "Type_in_Contact_email",
        "answer": contact_email,
    })

    # Retail Setup Pricing
    answers.append({
        "question": "Type_in_Retail_Setup_Pricing_for_Build_Plan~h~$50.00_or_greater_requires_Finance_Approval~num",
        "answer": build_price,
    })
    answers.append({
        "question": "Type_in_Retail_Setup_Pricing_for_Protect_Plan~h~$50.00_or_greater_requires_Finance_Approval~num",
        "answer": protect_price,
    })

    return answers


def process_draft(row: dict) -> dict:
    """Call the AxDraft API to generate a document with pre-filled answers.

    Posts to /api/customers/process-draft with the auth token, document
    template ID, and answers array built from CSV data.

    Args:
        row: A dict from csv.DictReader with the CSV columns.

    Returns:
        API response dict with "redirectUrl" on success.
    """
    answers = build_answers(row)
    company_name = row["COMPANY_NAME"].strip()
    deal_id = row["DEAL_ID"].strip()

    payload = {
        "token": AXDRAFT_TOKEN,
        "documentId": AXDRAFT_DOCUMENT_ID,
        "documentName": f"Order Form - {company_name} - {deal_id}",
        "answers": answers,
        "email": row.get("REQUESTING_EMAIL", "").strip(),
    }

    print(f"  [1/2] Building answers ({len(answers)} fields)...")
    print(f"        Document: Order Form - {company_name} - {deal_id}")
    print(f"        Template ID: {AXDRAFT_DOCUMENT_ID}")

    print(f"  [2/2] Calling AxDraft process-draft API...")
    url = f"{AXDRAFT_BASE_URL}/api/customers/process-draft"
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "ConsumerDirect-OnitAPI/1.0",
    }

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.load(resp)
            print(f"        Success! Redirect URL: {result.get('redirectUrl', 'N/A')}")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"        HTTP {e.code}: {error_body}")
        return {"success": False, "error": error_body, "status": e.code}


def start_axdraft(csv_path: str):
    """Read CSV and call AxDraft API for each row.

    This replaces the manual questionnaire flow. For each row, it builds
    the answers from CSV data and POSTs to the AxDraft process-draft API.

    Args:
        csv_path: Path to the CSV file with deal data.
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_name = row["COMPANY_NAME"].strip()
            deal_id = row["DEAL_ID"].strip()

            print(f"\n{'='*60}")
            print(f"  AxDraft: {company_name}  |  Deal {deal_id}")
            print(f"{'='*60}")

            result = process_draft(row)

            if result.get("redirectUrl"):
                print(f"\n  Done! Document URL:")
                print(f"  {result['redirectUrl']}")
            elif not result.get("success", True):
                print(f"\n  FAILED — see error above")
