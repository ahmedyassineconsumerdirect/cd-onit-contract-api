# Onit CLM Automation

Automates the Consumer Direct contract lifecycle in Onit App Builder: create contracts from CSV, generate Order Form documents via AxDraft, and send for HelloSign signature.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
ONIT_BASE_URL=https://your-instance.onit.com
ONIT_API_KEY=your_api_token
```

## Workflow

The automation runs in three steps:

### Step 1 — Create Contracts

```bash
python onit_client.py create-contract data/your_file.csv
```

Reads a Snowflake/HubSpot CSV export and creates a CLM contract for each row. Looks up the Other Party Contact by email (must already exist in Onit).

**Required CSV columns:** `COMPANY_NAME`, `CONTACT_NAME`, `CONTACT_EMAIL`, `DEAL_ID`, `REQUESTING_EMAIL`

### Step 2 — Generate Order Form (AxDraft)

```bash
python onit_client.py start-axdraft <atom_id>
```

Triggers the "Start AxDraft Contract" reaction which opens the AxDraft document generation flow. Currently requires manual completion in the AxDraft UI.

### Step 3 — Send for Signature (HelloSign)

```bash
python onit_client.py send-for-signature <atom_id>
```

Finds the Order Form document, creates a Send for Signature atom with two signers (Other Party Contact + Sales Operations), and triggers HelloSign to send signature request emails.

## Utility Commands

```bash
python onit_client.py list-apps                              # List all app dictionaries
python onit_client.py app-details <dictionary_id>            # Get field definitions for an app
python onit_client.py list-atoms <dictionary_id>             # List all records in an app
python onit_client.py get-atom <atom_id>                     # Get all fields for a record
python onit_client.py execute-reaction <atom_id> <name>      # Fire a reaction on a record
```

## Project Structure

```
onit_client.py        CLI entry point
src/
  config.py           Environment variables and dictionary IDs
  api.py              Low-level Onit REST API helpers
  lookups.py          Contact and document lookup helpers
  contracts.py        Step 1: Create contracts from CSV
  axdraft.py          Step 2: Trigger AxDraft document generation
  signature.py        Step 3: Send for HelloSign signature
  utils.py            Utility commands for exploring Onit data
data/                 CSV files
docs/                 API documentation and reference files
```
