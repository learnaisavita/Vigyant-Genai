import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from mcp.server import MCPServer


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


SPREADSHEET_ID = os.getenv(
    "GOOGLE_SPREADSHEET_ID",
    "",
).strip()


credentials_path = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "credentials/service-account.json",
)

CREDENTIALS_FILE = Path(credentials_path)

if not CREDENTIALS_FILE.is_absolute():
    CREDENTIALS_FILE = BASE_DIR / CREDENTIALS_FILE


READONLY_SCOPE = (
    "https://www.googleapis.com/auth/spreadsheets.readonly"
)


# IMPORTANT:
# Create MCP Server exactly ONCE
mcp = MCPServer("google-sheets-mcp-server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""

    return a + b


@mcp.tool()
def health_check() -> dict[str, Any]:
    """Check whether the MCP server is running."""

    return {
        "status": "ready",
        "spreadsheet_configured": bool(SPREADSHEET_ID),
        "credentials_found": CREDENTIALS_FILE.exists(),
    }


def get_sheets_service():
    """Create Google Sheets API client."""

    if not SPREADSHEET_ID:
        raise ValueError(
            "GOOGLE_SPREADSHEET_ID is not configured."
        )

    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"Credentials file not found: {CREDENTIALS_FILE}"
        )

    credentials = Credentials.from_service_account_file(
        str(CREDENTIALS_FILE),
        scopes=[READONLY_SCOPE],
    )

    return build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )


@mcp.tool()
def test_sheets_connection() -> dict[str, Any]:
    """Test connection to the configured Google spreadsheet."""

    service = get_sheets_service()

    result = (
        service
        .spreadsheets()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            fields=(
                "spreadsheetId,"
                "properties.title,"
                "sheets.properties.title"
            ),
        )
        .execute()
    )

    sheet_names = [
        sheet["properties"]["title"]
        for sheet in result.get("sheets", [])
    ]

    return {
        "status": "success",
        "spreadsheet_id": result.get("spreadsheetId"),
        "spreadsheet_title": result.get(
            "properties",
            {},
        ).get("title"),
        "sheet_names": sheet_names,
    }


@mcp.tool()
def read_sheet(
    range_name: str,
    max_rows: int = 100,
) -> dict[str, Any]:
    """Read values from a Google Sheets A1 range."""

    range_name = range_name.strip()

    if not range_name:
        raise ValueError("range_name cannot be empty.")

    if max_rows < 1 or max_rows > 1000:
        raise ValueError(
            "max_rows must be between 1 and 1000."
        )

    service = get_sheets_service()

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
        )
        .execute()
    )

    values = result.get("values", [])
    values = values[:max_rows]

    return {
        "status": "success",
        "range": result.get("range", range_name),
        "rows_returned": len(values),
        "values": values,
    }
