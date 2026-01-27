#!/usr/bin/env python3
"""Debit Card Limit Management MCP Server - Mock data from JSON files."""

import json
import sys
from pathlib import Path

from fastmcp import FastMCP

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_CARD_ID = "CARD-001"

mcp = FastMCP("Card Limit Manager 💳")


def load_json(filename: str) -> dict | list:
    return json.loads((DATA_DIR / filename).read_text())


def save_json(filename: str, data: dict | list) -> None:
    (DATA_DIR / filename).write_text(json.dumps(data, indent=2))


@mcp.tool()
def get_payment_instruments() -> dict:
    """Retrieve all user accounts and associated debit cards with their current limits."""
    accounts = load_json("accounts.json")
    limits = load_json("limits.json")
    temp_limits = load_json("temporary_limits.json")

    for account in accounts:
        for card in account["cards"]:
            card["currentLimits"] = limits.get(card["cardId"], {})
            card["temporaryLimits"] = temp_limits.get(card["cardId"], [])

    return {"accounts": accounts}


@mcp.tool()
def get_current_limits() -> dict:
    """Get current limits for the default card."""
    limits = load_json("limits.json")
    temp_limits = load_json("temporary_limits.json")

    return {
        "cardId": DEFAULT_CARD_ID,
        "limits": limits.get(DEFAULT_CARD_ID, {}),
        "temporaryLimits": temp_limits.get(DEFAULT_CARD_ID, []),
    }


@mcp.tool()
def change_limit(limit_type: str, limit: int) -> dict:
    """
    Change a card transaction limit.

    Args:
        limit_type: Type of limit to change. Must be one of:
            - "pos": POS / Point of Sale / in-store payment limit
            - "atm": ATM / cash withdrawal limit
            - "ecom": E-commerce / online payment limit
        limit: New limit amount in dollars
    """
    if limit_type not in ("pos", "atm", "ecom"):
        return {"error": f"Invalid limit_type: {limit_type}. Must be pos, atm, or ecom"}
    
    limits = load_json("limits.json")
    old = limits[DEFAULT_CARD_ID][limit_type]
    limits[DEFAULT_CARD_ID][limit_type] = limit
    save_json("limits.json", limits)
    return {"cardId": DEFAULT_CARD_ID, "type": limit_type, "old": old, "new": limit}


@mcp.tool()
def create_temporary_limit(limit_type: str, limit: int, start_date: str, end_date: str) -> dict:
    """
    Create a temporary card transaction limit override.

    Args:
        limit_type: Type of limit to override. Must be one of:
            - "pos": POS / Point of Sale / in-store payment limit
            - "atm": ATM / cash withdrawal limit
            - "ecom": E-commerce / online payment limit
        limit: Temporary limit amount in dollars
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    if limit_type not in ("pos", "atm", "ecom"):
        return {"error": f"Invalid limit_type: {limit_type}. Must be pos, atm, or ecom"}
    
    temp_limits = load_json("temporary_limits.json")
    entry = {"type": limit_type, "limit": limit, "startDate": start_date, "endDate": end_date}
    temp_limits[DEFAULT_CARD_ID].append(entry)
    save_json("temporary_limits.json", temp_limits)
    return {"cardId": DEFAULT_CARD_ID, "created": entry}


if __name__ == "__main__":
    print("Starting MCP Server on http://localhost:2009/mcp", file=sys.stderr)
    mcp.run(transport="http", host="0.0.0.0", port=2009, path="/mcp")
