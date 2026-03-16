"""
Lookup helpers for finding Onit records by field values.

These functions wrap the filter_atoms() API call with the specific
dictionary and field names needed for common lookups in the CLM workflow.

Both functions are used as prerequisites before creating or linking records:
  - lookup_contact_id: needed before create_contract (Step 1)
  - lookup_document_id: needed before send_for_signature (Step 3)
"""

from src.api import filter_atoms
from src.config import CONTACTS_DICTIONARY_ID, DOCUMENTS_DICTIONARY_ID, ORDER_FORM_DOC_NAME


def lookup_contact_id(contact_email: str) -> str:
    """Search the Other Party Contacts app by email address.

    The Other Party Contact record must already exist in Onit before
    a contract can be created. This function finds the contact's record ID
    which is required for the p_other_party_select_contact field.

    Args:
        contact_email: The contact's email address (e.g. "ahmed@consumerdirect.com")

    Returns:
        The contact record ID (UUID string), or "" if no match found.
    """
    records = filter_atoms(CONTACTS_DICTIONARY_ID, "p_email", contact_email)
    return records[0]["_id"] if records else ""


def lookup_document_id(contract_atom_id: str) -> str:
    """Find the Order Form document ID attached to a contract.

    After AxDraft generates the Order Form, it creates a document record
    in the Documents app linked to the contract via p_parent_id. This
    function finds that document so it can be passed to Send for Signature.

    When multiple documents exist (Onit auto-generates a placeholder on
    contract creation), this prefers the one with "Order Form" in the name.

    Args:
        contract_atom_id: The CLM contract atom ID to find documents for

    Returns:
        The document record ID (UUID string), or "" if no documents found.
    """
    records = filter_atoms(DOCUMENTS_DICTIONARY_ID, "p_parent_id", contract_atom_id)
    if not records:
        return ""
    for rec in records:
        if ORDER_FORM_DOC_NAME in rec.get("name", ""):
            return rec["_id"]
    return records[0]["_id"]
