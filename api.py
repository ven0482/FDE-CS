"""FastAPI backend: receives a ticket, searches history, returns suggestions."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from database import get_all_tickets, initialize_database
from matcher import find_similar_tickets
from models import TicketSearchRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run once when the API starts: create the database and load sample records.
    initialize_database()
    yield


app = FastAPI(
    title="Support Ticket Similarity API",
    description="Find similar resolved tickets to help support agents investigate faster.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """Simple endpoint to confirm the API is running."""
    return {"status": "ok", "service": "support-ticket-similarity-api"}


@app.get("/tickets")
def list_tickets():
    """Return historical tickets stored in SQLite."""
    return {"count": len(get_all_tickets()), "tickets": get_all_tickets()}


@app.post("/search")
def search_similar_tickets(request: TicketSearchRequest):
    """Find relevant old tickets and include their resolution notes."""
    subject = request.subject.strip()
    description = request.description.strip()
    if not subject or not description:
        raise HTTPException(status_code=422, detail="Subject and description are required.")

    new_ticket = {
        "ticket_id": request.ticket_id,
        "subject": subject,
        "description": description,
    }
    historical_tickets = get_all_tickets()
    result = find_similar_tickets(
        new_ticket,
        historical_tickets,
        limit=request.limit,
        threshold=request.threshold,
    )
    result["searched_ticket"] = new_ticket
    result["historical_ticket_count"] = len(historical_tickets)
    return result
