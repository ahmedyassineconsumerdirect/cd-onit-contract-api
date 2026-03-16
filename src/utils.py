"""
Utility commands for exploring and debugging the Onit API.

These are helper commands for inspecting Onit data during development.
They print JSON responses directly to stdout for easy inspection.

Commands:
    list_apps()                  - List all app dictionaries (shows app names + IDs)
    app_details(dictionary_id)   - Get full field definitions for an app (shows all
                                   atom_properties with data types, required flags, etc.)
    list_atoms(dictionary_id)    - List all records in an app (shows name + _id for each)
    get_atom(atom_id)            - Get all fields for a single record
    execute_reaction(atom_id, name) - Fire a named reaction/action on a record
"""

import json
import urllib.parse

from src.api import api_request


def list_apps():
    """List all Onit App Builder dictionaries (apps).

    Useful for discovering available apps and their dictionary IDs.
    """
    print(json.dumps(api_request("GET", "/api/atom_dictionaries.json"), indent=2))


def app_details(dictionary_id: str):
    """Get full field definitions for an Onit app.

    Shows all atom_properties including field names, data types,
    required flags, default values, and dropdown options. Useful
    for figuring out what fields an app expects.

    Args:
        dictionary_id: The app dictionary ID (e.g. "54b7e691ed404f54990003bf")
    """
    print(json.dumps(api_request("GET", f"/api/atom_dictionaries/{dictionary_id}.json"), indent=2))


def list_atoms(dictionary_id: str):
    """List all records (atoms) in an Onit app.

    Returns name and _id for each record. Useful for browsing
    existing records or finding specific ones.

    Args:
        dictionary_id: The app dictionary ID to list records from
    """
    print(json.dumps(api_request("GET", f"/api/atom_dictionaries/{dictionary_id}/atoms.json"), indent=2))


def get_atom(atom_id: str):
    """Get all fields for a single Onit record.

    Returns the complete atom with all p_ (property) and r_ (relationship)
    fields. Useful for inspecting what data a record contains.

    Args:
        atom_id: The atom/record UUID
    """
    print(json.dumps(api_request("GET", f"/api/atoms/{atom_id}.json"), indent=2))


def execute_reaction(atom_id: str, reaction_name: str):
    """Fire a named reaction (action button) on an Onit record.

    Reactions are workflow actions configured in Onit App Builder.
    The reaction name is URL-encoded since it may contain spaces.

    Args:
        atom_id:       The atom/record UUID to execute the reaction on
        reaction_name: The reaction name (e.g. "Start AxDraft Contract")
    """
    encoded = urllib.parse.quote(reaction_name)
    result = api_request("PUT", f"/api/atoms/{atom_id}/execute_reaction/?reaction_name={encoded}")
    print(json.dumps(result, indent=2))
