# Card Limit Manager 💳

A Model Context Protocol (MCP) server for managing debit card transaction limits including POS payments, ATM withdrawals, and E-commerce purchases. Built with [FastMCP](https://github.com/jlopp/fastmcp).

## Features

- **Get Payment Instruments**: Retrieve all accounts and cards with current limits
- **Get Current Limits**: View limits for the default card
- **Change Transaction Limits**: Update permanent limits for POS, ATM, or E-commerce transactions
- **Create Temporary Limits**: Set temporary limit overrides with start and end dates
- **Mock Data**: All data is stored in JSON files for easy testing and modification

## Project Structure

```
.
├── fastmcp_server.py           # MCP server implementation
├── requirements.txt            # Python dependencies
├── openapi.yaml               # API specification
├── README.md                  # This file
└── data/
    ├── accounts.json          # Account and card information
    ├── limits.json            # Current transaction limits
    └── temporary_limits.json   # Active temporary limit overrides
```

## Setup

### Prerequisites

- Python 3.8+
- FastMCP

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Running the Server

```bash
python fastmcp_server.py
```

The server will start on `http://localhost:2009/mcp`

## Available Tools

### `get_payment_instruments()`

Retrieve all user accounts and associated debit cards with their current limits.

**Response:**
```json
{
  "accounts": [
    {
      "accountId": "ACC-001",
      "accountNumber": "****5678",
      "accountType": "checking",
      "balance": 15000.00,
      "currency": "USD",
      "cards": [
        {
          "cardId": "CARD-001",
          "cardNumber": "****1234",
          "cardHolderName": "John Doe",
          "cardType": "debit",
          "status": "active",
          "currentLimits": {
            "pos": 1000,
            "atm": 500,
            "ecom": 2000
          },
          "temporaryLimits": []
        }
      ]
    }
  ]
}
```

### `get_current_limits()`

Get current limits for the default card (CARD-001).

**Response:**
```json
{
  "cardId": "CARD-001",
  "limits": {
    "pos": 1000,
    "atm": 500,
    "ecom": 2000
  },
  "temporaryLimits": []
}
```

### `change_limit(limit_type, limit)`

Change a card transaction limit.

**Parameters:**
- `limit_type` (string): Type of limit - `"pos"`, `"atm"`, or `"ecom"`
- `limit` (integer): New limit amount in dollars

**Example:**
```json
{
  "limit_type": "pos",
  "limit": 1500
}
```

**Response:**
```json
{
  "cardId": "CARD-001",
  "type": "pos",
  "old": 1000,
  "new": 1500
}
```

### `create_temporary_limit(limit_type, limit, start_date, end_date)`

Create a temporary transaction limit override.

**Parameters:**
- `limit_type` (string): Type of limit - `"pos"`, `"atm"`, or `"ecom"`
- `limit` (integer): Temporary limit amount in dollars
- `start_date` (string): Start date in YYYY-MM-DD format
- `end_date` (string): End date in YYYY-MM-DD format

**Example:**
```json
{
  "limit_type": "atm",
  "limit": 1000,
  "start_date": "2026-01-27",
  "end_date": "2026-02-01"
}
```

**Response:**
```json
{
  "cardId": "CARD-001",
  "created": {
    "type": "atm",
    "limit": 1000,
    "startDate": "2026-01-27",
    "endDate": "2026-02-01"
  }
}
```

## Data Files

### `data/accounts.json`

Contains account information and card details. Modify this file to add/update accounts and cards.

### `data/limits.json`

Stores current transaction limits per card. Updated when `change_limit()` is called.

```json
{
  "CARD-001": {
    "pos": 1000,
    "atm": 500,
    "ecom": 2000
  }
}
```

### `data/temporary_limits.json`

Stores active temporary limit overrides. Updated when `create_temporary_limit()` is called.

```json
{
  "CARD-001": [
    {
      "type": "pos",
      "limit": 1500,
      "startDate": "2026-01-27",
      "endDate": "2026-02-01"
    }
  ]
}
```

## Limit Types

- **`pos`**: Point of Sale / in-store payment limit
- **`atm`**: ATM / cash withdrawal limit
- **`ecom`**: E-commerce / online payment limit

## Default Card

The server operates on a default card (CARD-001) for limit operations. To change the default card, modify the `DEFAULT_CARD_ID` constant in `fastmcp_server.py`.

## Testing

You can test the API using curl:

```bash
# Get payment instruments
curl -X GET http://localhost:2009/mcp/tools/get_payment_instruments

# Change a limit
curl -X POST http://localhost:2009/mcp/tools/change_limit \
  -H "Content-Type: application/json" \
  -d '{"limit_type": "pos", "limit": 2000}'

# Create a temporary limit
curl -X POST http://localhost:2009/mcp/tools/create_temporary_limit \
  -H "Content-Type: application/json" \
  -d '{
    "limit_type": "atm",
    "limit": 1500,
    "start_date": "2026-01-27",
    "end_date": "2026-02-10"
  }'
```

## License

MIT
