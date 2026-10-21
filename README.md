# Support Ticket Similarity Assistant

A beginner-friendly FDE case-study prototype using **FastAPI + Streamlit + SQLite**.

The goal is to help a support agent find older tickets that look like a new customer issue, review how the older issue was resolved, and decide what to investigate next. The tool suggests evidence; it does not automatically answer the customer or close a ticket.

## 1. What is included?

- `app.py` — Streamlit page the support agent uses.
- `api.py` — FastAPI service that receives a search request and returns matching tickets.
- `database.py` — creates the SQLite database and reads the saved tickets.
- `matcher.py` — simple word-overlap matching logic with comments.
- `models.py` — validates the search request.
- `data/tickets.json` — 12 illustrative historical tickets so the demo runs immediately.
- `data/new_tickets_example.json` — four incoming-ticket examples from the supplied starter material.
- `tests/test_matcher.py` — tests for matches and the no-match case.
- `SOLUTION_DESIGN.md` — architecture, assumptions, trade-offs, and next steps.
- `PRESENTATION_GUIDE.md` — a panel-ready walkthrough and sample answers in a healthcare-enterprise style.

**Dataset note:** The supplied starter README says the original historical file contains about 40 tickets, but that original `tickets.json` was not present in the files available for this build. The included 12-ticket history is synthetic demo data. Replace `data/tickets.json` with the original historical dataset before presenting any results as results from the starter dataset. The four incoming examples were copied from the supplied `new_tickets_example.json`.

## 2. How the pieces work

1. The agent enters a subject and description in Streamlit.
2. Streamlit sends the text to FastAPI over HTTP.
3. FastAPI reads historical tickets from SQLite.
4. `matcher.py` compares important words in the new ticket with each old ticket.
5. FastAPI returns the highest-scoring matches, shared words, and resolution notes.
6. Streamlit displays the suggestions. If nothing passes the threshold, it says no strong match was found.

```text
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
```

## 3. Run it locally

Use Python 3.10 or newer. Open a terminal in this folder.

### Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Terminal 1 — start the API

```bash
uvicorn api:app --reload
```

Open `http://127.0.0.1:8000/health` to see the health check. Open `http://127.0.0.1:8000/docs` to try the API interactively.

The first API startup creates `tickets.db` and loads the sample historical tickets. SQLite is a local file; you do not need to install a separate database server.

### Terminal 2 — start the user interface

Keep Terminal 1 running. Open a second terminal in the same project folder, activate the same virtual environment, then run:

```bash
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## 4. Suggested demo

1. Select **NT-1** from the sidebar and click **Load selected example**.
2. Click **Find similar tickets**. Explain that the result includes the old issue, resolution notes, score, and shared words.
3. Repeat with **NT-2** (revenue chart) and **NT-3** (duplicate billing).
4. Try **NT-4** (Snowflake). With the default threshold, it may show no strong match; if it does show a weak match, increase the minimum similarity. The intended behavior is not to force a match when evidence is weak.
5. Click **Show historical ticket count** to show that the records are stored in SQLite.
6. Open `http://127.0.0.1:8000/docs` to show the API separately from the UI.

## 5. How similarity works (simple explanation)

The matcher removes common filler words, compares the remaining words, and calculates:

`score = number of shared words / number of unique words across both tickets`

This is called Jaccard similarity. A score closer to 1 means more overlap. A score is **not** a probability that the tickets are the same. The default minimum is `0.08` for this small demo dataset; it must be tuned and evaluated with real examples before production use.

## 6. Run tests

```bash
pytest -q
```

The tests check the main examples and confirm that the Snowflake example can return no strong match. They test the matching function, not production readiness or real-world business outcomes.

## 7. Important limitations

- This is a prototype, not a production-ready support platform.
- Matching is based on word overlap. It may miss synonyms and may match tickets that share words but have different causes.
- Sample history is synthetic; test with the actual historical dataset before drawing conclusions.
- No customer data, credentials, external LLM, or third-party AI service is required.
- Authentication, role-based access, audit logs, monitoring, encryption, data retention, and deployment configuration are not included.
- Agents must review the old resolution and confirm that it applies to the current customer.
