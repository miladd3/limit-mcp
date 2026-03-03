#!/usr/bin/env python3
"""Debit Card Limit Management MCP Server backed by limit-api."""

import os
import sys
from urllib import error, request

import json

from fastmcp import FastMCP

DEFAULT_CARD_ID = "CARD-001"
DEFAULT_API_BASE_URL = "http://127.0.0.1:2010"

mcp = FastMCP("Card Limit Manager 💳")


def get_api_base_url() -> str:
    return os.getenv("LIMIT_API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


def call_api(method: str, path: str, payload: dict | None = None) -> dict:
    base_url = get_api_base_url()
    url = f"{base_url}{path}"
    body = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url=url, data=body, method=method, headers=headers)
    try:
        with request.urlopen(req, timeout=10) as response:
            raw_body = response.read().decode("utf-8")
            return json.loads(raw_body) if raw_body else {}
    except error.HTTPError as exc:
        # Normalize API error payloads for MCP clients.
        response_body = exc.read().decode("utf-8") if exc.fp else ""
        parsed = {}
        if response_body:
            try:
                parsed = json.loads(response_body)
            except json.JSONDecodeError:
                parsed = {}
        detail = parsed.get("detail") if isinstance(parsed, dict) else None
        return {
            "error": detail or f"API returned HTTP {exc.code}",
            "status": exc.code,
        }
    except error.URLError as exc:
        return {
            "error": "Could not reach limit-api. Ensure it is running.",
            "details": str(exc.reason),
            "apiBaseUrl": base_url,
        }


@mcp.tool()
def get_payment_instruments() -> dict:
    """Retrieve all user accounts and associated debit cards with their current limits."""
    return call_api("GET", "/accounts")


@mcp.tool()
def get_current_limits() -> dict:
    """Get current limits for the default card."""
    return call_api("GET", "/cards/default/limits")


@mcp.tool()
def change_limit(limit_type: str, limit: int) -> dict:
    """
    Change a card transaction limit.

    Args:
        limit_type: Type of limit to change. Must be one of:
            - "pos": POS / Point of Sale / in-store payment limit
            - "atm": ATM / cash withdrawal limit
            - "ecom": E-commerce / online payment limit
        limit: New limit amount in euros
    """
    if limit_type not in ("pos", "atm", "ecom"):
        return {"error": f"Invalid limit_type: {limit_type}. Must be pos, atm, or ecom"}

    return call_api(
        "PATCH",
        f"/cards/{DEFAULT_CARD_ID}/limits/{limit_type}",
        payload={"limit": limit},
    )


@mcp.tool()
def create_temporary_limit(limit_type: str, limit: int, start_date: str, end_date: str) -> dict:
    """
    Create a temporary card transaction limit override.

    Args:
        limit_type: Type of limit to override. Must be one of:
            - "pos": POS / Point of Sale / in-store payment limit
            - "atm": ATM / cash withdrawal limit
            - "ecom": E-commerce / online payment limit
        limit: Temporary limit amount in euros
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    if limit_type not in ("pos", "atm", "ecom"):
        return {"error": f"Invalid limit_type: {limit_type}. Must be pos, atm, or ecom"}

    return call_api(
        "POST",
        f"/cards/{DEFAULT_CARD_ID}/temporary-limits/{limit_type}",
        payload={"limit": limit, "startDate": start_date, "endDate": end_date},
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 2009))
    print(
        f"Starting MCP Server on http://0.0.0.0:{port}/mcp (API: {get_api_base_url()})",
        file=sys.stderr,
    )
    mcp.run(transport="http", host="0.0.0.0", port=port, path="/mcp")
