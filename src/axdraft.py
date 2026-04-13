"""
Step 2: Generate the Order Form document via the AxDraft API.

Instead of manually filling in the AxDraft questionnaire, this calls the
AxDraft process-draft API with pre-filled answers built from the CSV data.

The AxDraft API expects an array of {question, answer} pairs where:
  - "question" is the AxDraft variable name (Column B from the field mapping spreadsheet)
  - "answer" is the selected value

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

    # --- Selection Questions ---

    # Deal complexity: Standard for automated flow
    answers.append({
        "question": "select_What_is_the_complexity_of_deal?",
        "answer": "Standard",
    })

    # New order form (not changing an existing one)
    answers.append({
        "question": "select_Do_you_want_to_generate_a_new_order_form_or_change_an_executed_order?",
        "answer": "Generate a new order form",
    })

    # Deal type from CSV PARTNER_TYPE
    answers.append({
        "question": "select_What_is_the_deal_type?",
        "answer": partner_type,
    })

    # Pricing model — Partnership uses Transactional, White Label uses Bundle
    pricing = "Bundle Pricing" if partner_type == "White Label" else "Transactional Pricing"
    answers.append({
        "question": "select_What_is_the_Pricing?",
        "answer": pricing,
    })

    # ConsumerDirect Merchant Processor — No by default
    answers.append({
        "question": "select_Are_you_adding_ConsumerDirect_Merchant_Processor?",
        "answer": "No",
    })

    # myLONA Rev Share — No by default
    answers.append({
        "question": "select_Do_you_want_to_add_myLONA_Rev_Share?",
        "answer": "No",
    })

    # Standard prices for Plan Licensing Fees — Yes (using standard)
    answers.append({
        "question": "select_Do_you_want_to_use_standard_prices_for_Plan_Licensing_Fees?",
        "answer": "Yes",
    })

    # Ramp Up Pricing — No by default
    answers.append({
        "question": "select_Do_you_want_to_add_on_Ramp_Up_Pricing?",
        "answer": "No",
    })

    # Standard price for 3 Bureau Credit Report — Yes
    answers.append({
        "question": "select_Do_you_want_to_use_standard_price_for_3_Bureau_Credit_Report_and_Scores?",
        "answer": "Yes",
    })

    # Further revisions — No
    answers.append({
        "question": "select_Are_there_any_further_revisions_required_beyond_what_was_previously_addressed?",
        "answer": "No",
    })

    # Product
    answers.append({
        "question": "select_What_is_the_Product?",
        "answer": "The Lending Score",
    })

    # Plan — Plan A default
    answers.append({
        "question": "select_Choose_Plan:",
        "answer": "Plan A",
    })

    # Customer Service — No by default
    answers.append({
        "question": "select_Do_you_want_ConsumerDirect_to_provide_Customer_Service_for_Partner_Clients?",
        "answer": "No",
    })

    # Trial period from CSV
    answers.append({
        "question": "select_Are_you_including_a_trial_period?",
        "answer": trial_selection,
    })

    # Exclusivity — No by default
    answers.append({
        "question": "select_Is_this_an_Exclusivity_Relationship?",
        "answer": "No",
    })

    # Standard Setup Promo fee — Yes
    answers.append({
        "question": "select_Do_you_want_to_use_standard_Setup_Promo_fee?",
        "answer": "Yes",
    })

    # Standard Additional Tracking Link promo fee — Yes
    answers.append({
        "question": "select_Do_you_want_to_use_standard_Additional_Tracking_Link_promo_fee?",
        "answer": "Yes",
    })

    # W9 form — No
    answers.append({
        "question": "select_Do_you_want_to_add_W9_form?",
        "answer": "No",
    })

    # Supersede legacy agreement — No
    answers.append({
        "question": "select_Does_this_Order_Form_supersede_a_previous_legacy_agreement?",
        "answer": "No",
    })

    # Disable action buttons — No
    answers.append({
        "question": "select_Do_you_want_to_disable_the_action_buttons?",
        "answer": "No",
    })

    # Sponsored Plan — No
    answers.append({
        "question": "select_Are_you_adding_a_Sponsored_Plan_option?",
        "answer": "No Sponsored Plan",
    })

    # Hide a Plan — No
    answers.append({
        "question": "select_Do_you_want_to_hide_a_Plan?",
        "answer": "No",
    })

    # Discounts/promos — No promos by default
    answers.append({
        "question": "Please_select_discounts_and_promos_if_applicable",
        "answer": "No promos",
    })

    # Standard price for 1 Bureau Credit Report — Yes
    answers.append({
        "question": "select_Do_you_want_to_use_standard_price_for_1_Bureau_Credit_Report_and_Scores?",
        "answer": "Yes",
    })

    # Standard price for $1MM Family Fraud Insurance — Yes
    answers.append({
        "question": "select_Do_you_want_to_use_standard_price_for_$1MM_Family_Fraud_Insurance?",
        "answer": "Yes",
    })

    # Standard price for PrivacyMaster — Yes
    answers.append({
        "question": "select_Do_you_want_to_use_standard_price_for_PrivacyMaster?",
        "answer": "Yes",
    })

    # Standard Development Promo Fee — Yes
    answers.append({
        "question": "Do_you_want_to_use_standard_Development_Promo_Fee?",
        "answer": "Yes",
    })

    # --- Input Fields ---

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

    # Retail Setup Pricing for Build Plan
    answers.append({
        "question": "Type_in_Retail_Setup_Pricing_for_Build_Plan~h~$50.00_or_greater_requires_Finance_Approval~num",
        "answer": build_price,
    })

    # Retail Setup Pricing for Protect Plan
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
        "documendId": AXDRAFT_DOCUMENT_ID,  # Note: typo is in the AxDraft API spec
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
    headers = {"Content-Type": "application/json"}

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
