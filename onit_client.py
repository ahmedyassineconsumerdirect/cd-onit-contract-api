"""
Onit CLM Automation Client

Workflow:
    python onit_client.py create-contract <csv_path>     Step 1: Create CLM contracts from CSV
    python onit_client.py start-axdraft <atom_id>        Step 2: Trigger AxDraft document generation
    python onit_client.py send-for-signature <atom_id>   Step 3: Send contract for HelloSign signature

Utility:
    python onit_client.py get-atom <atom_id>             Get atom details
    python onit_client.py list-apps                      List all app dictionaries
    python onit_client.py app-details <dictionary_id>    Get app field definitions
    python onit_client.py list-atoms <dictionary_id>     List atoms in an app
    python onit_client.py execute-reaction <atom_id> <reaction_name>
"""

import sys

from src.contracts import create_contract
from src.axdraft import start_axdraft
from src.signature import send_for_signature
from src.utils import list_apps, app_details, list_atoms, get_atom, execute_reaction


COMMANDS = {
    # Workflow
    "create-contract":    (1, lambda args: create_contract(args[0])),
    "start-axdraft":      (1, lambda args: start_axdraft(args[0])),       # now takes CSV path
    "send-for-signature": (1, lambda args: send_for_signature(args[0])),
    # Utility
    "get-atom":           (1, lambda args: get_atom(args[0])),
    "list-apps":          (0, lambda args: list_apps()),
    "app-details":        (1, lambda args: app_details(args[0])),
    "list-atoms":         (1, lambda args: list_atoms(args[0])),
    "execute-reaction":   (2, lambda args: execute_reaction(args[0], args[1])),
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

    min_args, fn = COMMANDS[cmd]
    if len(args) < min_args:
        print(f"Usage: python onit_client.py {cmd} {'<arg> ' * min_args}")
        sys.exit(1)

    fn(args)


if __name__ == "__main__":
    main()
