"""
Low-level Onit REST API helpers.

All communication with the Onit App Builder API goes through this module.
Authentication is handled automatically by appending the auth_token query
parameter to every request.

The Onit API uses "atoms" (records) organized into "atom dictionaries" (apps).
Each atom has fields prefixed with p_ (properties) and r_ (relationships).

Rate limit: 30 requests per 10 seconds.
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional

from src.config import BASE_URL, API_KEY


def api_request(method: str, path: str, body: Optional[dict] = None) -> dict:
    """Make an authenticated request to the Onit API.

    Handles JSON serialization, auth token injection, and error handling.
    All API calls return {"success": bool, "data": ..., "message": ...}.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        path:   API path starting with / (e.g. "/api/atoms/<id>.json")
        body:   Optional dict to send as JSON body (for POST/PUT)

    Returns:
        Parsed JSON response dict. On HTTP errors, returns
        {"success": False, "message": "<error body>"}.
    """
    separator = "&" if "?" in path else "?"
    url = f"{BASE_URL}{path}{separator}auth_token={API_KEY}"

    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["content-type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"  HTTP {e.code}: {error_body}")
        return {"success": False, "message": error_body}


def filter_atoms(dictionary_id: str, field: str, value: str) -> list:
    """Search atoms in a dictionary by exact field match.

    Uses the Onit filter API to find records where a given field
    equals a specific value. This is the primary way to look up
    records by email, parent ID, etc.

    Args:
        dictionary_id: The app/dictionary to search in
        field:         The field name to filter on (e.g. "p_email", "p_parent_id")
        value:         The exact value to match

    Returns:
        List of matching atom dicts (each has at least "_id" and "name").
        Empty list if no matches found.

    Example:
        # Find contacts by email
        records = filter_atoms(CONTACTS_DICTIONARY_ID, "p_email", "ahmed@example.com")
    """
    filter_json = json.dumps([{
        "field": field, "type": "text",
        "comparison": "equals", "value": value,
    }])
    encoded = urllib.parse.quote(filter_json)
    result = api_request(
        "GET",
        f"/api/atom_dictionaries/{dictionary_id}/atoms.json?filter={encoded}",
    )
    return result.get("data", [])
