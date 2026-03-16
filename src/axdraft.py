"""
Step 2: Trigger AxDraft document generation.

After a contract is created (Step 1), this fires the "Start AxDraft Contract"
reaction on the CLM atom. This causes Onit to:

    1. Build a questionnaire JSON (p_axdraft_json) from the contract fields:
       - Type_in_Company_name, Type_in_Contact_firstname/lastname
       - Type_in_Contact_email, Type_in_Order_ID
       - Type_in_Company_address/city/state/ZIP, Type_in_Contact_phone

    2. Redirect to AxDraft (workspace 2422, template 14897) where the
       Order Form document is generated with pricing and deal terms.

    3. AxDraft pushes the completed document and pricing fields back to Onit:
       - Creates "Consumer Direct - Order Form.docx" in the Documents app
       - Populates deal_type, pricing tiers, trial period, etc.

Currently this step requires manual completion in the AxDraft UI after
the reaction is triggered. Full automation is pending the AxDraft API key
(see docs/Generation API Integration - AXDRAFT.docx).
"""

from src.utils import execute_reaction


def start_axdraft(atom_id: str):
    """Trigger the 'Start AxDraft Contract' reaction on a CLM atom.

    This fires the Onit reaction that initiates the AxDraft document
    generation flow.

    Args:
        atom_id: The CLM contract atom ID from Step 1.
    """
    print(f"Triggering 'Start AxDraft Contract' on {atom_id}...")
    execute_reaction(atom_id, "Start AxDraft Contract")
