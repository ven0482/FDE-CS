"""SQLite helpers for the Support Ticket Similarity Assistant.

This file keeps database work in one place so the rest of the project is easier
for a beginner to follow.
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "tickets.json"
# You can set TICKETS_DB_PATH to use a different database file.
DB_FILE = Path(os.getenv("TICKETS_DB_PATH", str(BASE_DIR / "tickets.db")))


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection and return rows like dictionaries."""
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """Create the table and load sample tickets the first time the app runs."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                resolution_notes TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_date TEXT NOT NULL
            )
            """
        )

        # Seed only when the table is empty. Existing saved tickets are kept.
        ticket_count = connection.execute(
            "SELECT COUNT(*) FROM tickets"
        ).fetchone()[0]
        if ticket_count == 0 and DATA_FILE.exists():
            with DATA_FILE.open("r", encoding="utf-8") as file:
                sample_data = json.load(file)

            for ticket in sample_data.get("tickets", []):
                connection.execute(
                    """
                    INSERT OR IGNORE INTO tickets
                    (ticket_id, subject, description, resolution_notes,
                     category, tags, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        ticket["ticket_id"],
                        ticket["subject"],
                        ticket["description"],
                        ticket.get("resolution_notes", ""),
                        ticket.get("category", "Other"),
                        json.dumps(ticket.get("tags", [])),
                        ticket.get("created_date", ""),
                    ),
                )


def get_all_tickets() -> list[dict[str, Any]]:
    """Read tickets from SQLite and convert each row to a normal dictionary."""
    with get_connection() as connection:
        rows = connection.execute(
            """SELECT ticket_id, subject, description, resolution_notes,
                      category, tags, created_date
               FROM tickets ORDER BY created_date DESC, ticket_id"""
        ).fetchall()

    tickets = []
    for row in rows:
        ticket = dict(row)
        ticket["tags"] = json.loads(ticket["tags"] or "[]")
        tickets.append(ticket)
    return tickets
