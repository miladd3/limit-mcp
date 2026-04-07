# Card Limit Manager 💳

A Model Context Protocol (MCP) server for managing debit card transaction limits including POS payments, ATM withdrawals, and E-commerce purchases. Built with [FastMCP](https://github.com/jlopp/fastmcp), and backed by the REST API in `../limit-api`.

## Features

- **Get Payment Instruments**: Retrieve all accounts and cards with current limits
- **Get Current Limits**: View limits for the default card
- **Change Transaction Limits**: Update permanent limits for POS, ATM, or E-commerce transactions
- **Create Temporary Limits**: Set temporary limit overrides with start and end dates
- **API-Backed**: All business logic and data access are delegated to `limit-api`

## Project Structure

```
.
├── fastmcp_server.py           # MCP server implementation
├── pyproject.toml              # Python project & dependencies
├── openapi.yaml               # API specification
├── README.md                  # This file
└── data/                       # Legacy mock files (no longer used by MCP runtime)
```

## Setup

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

### Installation

```bash
uv sync
```

## Running the Server

1. Start the REST API first:

```bash
cd /home/milad/Projects/limit-api
uv run uvicorn main:app --reload --host 0.0.0.0 --port 2010
```

2. Start the MCP server:

```bash
cd /home/milad/Projects/limit-mcp
uv run python fastmcp_server.py
```

The server will start on `http://localhost:2009/mcp`

By default, MCP calls `http://127.0.0.1:2010`. To target another API host:

```bash
LIMIT_API_BASE_URL=http://your-api-host:2010 uv run python fastmcp_server.py
```

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
- `limit` (integer): New limit amount in euros

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
- `limit` (integer): Temporary limit amount in euros
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

## Data Ownership

MCP does not read or write card-limit JSON files directly anymore.
All reads/writes happen through `limit-api`, which owns validation and persistence.

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
