# Solution Design — Support Ticket Similarity Assistant

## Problem

Support agents may spend time investigating an issue that was already resolved for another customer. They need a quick way to discover relevant historical tickets and review the earlier resolution. The system should also be honest when the history does not contain a useful example.

## Proposed MVP

A small web application with three clear parts:

- **Streamlit:** the agent-facing form and results page.
- **FastAPI:** a separate backend API that validates the request and runs the search.
- **SQLite:** a lightweight local database for historical ticket records.

The matching code is isolated in `matcher.py`, so it can be replaced later without rewriting the UI or database code.

## Request flow

1. Agent enters a new ticket subject and description.
2. Streamlit calls `POST /search` on FastAPI.
3. FastAPI validates the input using the Pydantic model.
4. The API loads historical records from SQLite.
5. The matcher calculates word-overlap scores and sorts matches.
6. The API returns the top matches above a configurable threshold.
7. Streamlit shows issue details, resolution notes, score, and shared words.
8. If no match meets the threshold, the UI advises the agent to investigate normally.

Support agent
    |
    v
Streamlit UI (app.py)
    | HTTP request
    v
FastAPI service (api.py)
    | reads ticket history
    v
SQLite database (tickets.db)
    |
    v
Matcher (matcher.py) -> ranked tickets + shared words
    |
    v
Streamlit shows prior resolution or a no-strong-match message


## Data model

The SQLite `tickets` table contains:

| Field | Purpose |
|---|---|
| `ticket_id` | Unique ticket identifier and primary key |
| `subject` | Short issue title |
| `description` | Customer's problem description |
| `resolution_notes` | How the historical issue was resolved |
| `category` | Support category |
| `tags` | Tags stored as JSON text |
| `created_date` | Historical ticket date |

## Matching approach

For this time-boxed prototype, normalize text into lowercase words, remove common filler words, and calculate Jaccard similarity:

`shared important words / all unique important words from both tickets`

Only tickets that pass the minimum threshold are returned. This approach is transparent and requires no API key, model download, or external service. It is not semantic understanding and does not know whether two issues have the same root cause.

## Key assumptions

- Historical tickets contain useful resolution notes.
- Subject, description, category, and tags are available for most records.
- A support agent, rather than the software, makes the final decision.
- For this prototype, a local SQLite file is enough.
- A low-confidence result should be treated as “no strong match,” not a forced recommendation.
- The original historical ticket file should be used for final evaluation; the included 12 tickets are demo fixtures only.

## Trade-offs

**Why SQLite?** It requires no database server, is easy to set up on a laptop, and is appropriate for a small single-user prototype. For a multi-user enterprise service, evaluate PostgreSQL or the organization's approved database.

**Why FastAPI?** It separates the matching service from the UI, provides request validation, and exposes API documentation at `/docs`.

**Why Streamlit?** It makes a usable demo quickly without requiring frontend JavaScript knowledge.

**Why word overlap?** It is easy to explain and debug. It will not understand synonyms, sentence meaning, or root cause. Semantic embeddings can be evaluated later against a labeled test set.

**Why show no match?** A weak suggestion can mislead an agent. Abstaining is safer than presenting an unrelated old resolution as if it were correct.

## What I would do with more time or budget

1. **Understand the business needs:** Work closely with support agents and team leads to understand their daily challenges, identify common ticket issues, and define how we will measure success.
2. **Improve data quality:** Review actual historical tickets, clean up incomplete or duplicate records, and make sure resolution notes are accurate and useful.
3. **Make ticket matching smarter:** Improve the current keyword-based approach using AI embeddings and semantic search, so the system can find similar issues even when customers describe them differently.
4. **Integrate with existing systems:** Connect the assistant to Solari Analytics' ticketing platform so agents can access previous resolutions directly and provide feedback on suggested matches.
5. **Test, secure, and scale:** Start with a small group of support agents, measure accuracy and time saved, add appropriate security controls, and gradually expand based on feedback and results.

## Risks and mitigations

- **Wrong match:** show the evidence words and original resolution; require agent judgment; tune the threshold on labeled data.
- **No useful result:** explicitly abstain and keep the normal investigation path available.
- **Stale or poor resolution notes:** show the original ticket date and allow agents to open the source record when integrated.
- **Sensitive customer content:** apply data minimization, access controls, and approved retention/security policies before using real tickets.
- **Prototype mistaken for production:** document limitations and measure quality before wider rollout.

## Success measures to validate with the business

- Precision of the top 3 suggested tickets, judged by support agents.
- Percentage of new tickets where agents find a useful prior case.
- Time from ticket opening to a confirmed investigation path.
- Agent adoption and feedback rate.
- Rate of misleading suggestions and rate of appropriate abstentions.

No business improvement is claimed by this prototype; these are measures to validate in a pilot.
