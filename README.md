# Customer Support Assistant

A text support agent for Empório da Música, a fictional musical instrument store in Campo Grande/MS. It answers questions about products, prices, promotions, orders, returns and store policies, and hands cases over to the store team when needed.

- Python 3.14
- LangGraph agent with tool calling
- FastAPI
- SQLite with SQLAlchemy
- OpenRouter as LLM provider
- React, Vite and TypeScript chat UI
- Docker Compose

With the default model, `google/gemini-3.8-flash`, an average customer message uses about **4,900 input tokens and 330 output tokens**, costs about **US$ 0.005** and takes about **7 seconds**. Measured over 23 messages in 19 test conversations billed by OpenRouter.

Example conversations: [`docs/example-conversations.md`](docs/example-conversations.md)

## Architecture

```
UI -> API -> Agent -> Tools -> Services -> Repositories -> SQLite
```

| Tool | Purpose |
|---|---|
| `search_products` | Catalog search with filters |
| `get_product_details` | Final price, promotion, PIX, installments, specs, alternatives |
| `get_order_status` | Verified order status and tracking |
| `check_return_eligibility` | Return, exchange and warranty deadlines for an order |
| `get_policy` | One section of the store manual |
| `get_current_datetime` | Current date, time and whether the store is open |
| `handoff_to_human` | Registers a case for the team |

Prompts live in `back-end/prompts/` as markdown files: the system prompt split by topic and one description per tool. Store values such as hours, installment tiers and return deadlines live in `back-end/config/store.toml`, so no store data is hardcoded.

## Features

- **Persona** based on the store manual: informal but professional, replies in the customer's language.
- **Product search** by category, brand, price range and promotion, with alternatives when an item is unavailable.
- **Pricing** with active promotions, PIX discount and installment simulation following the store rules.
- **Orders**: status, tracking and overdue delivery detection, only after verifying the order number plus the customer's email or phone.
- **Returns and warranty**: regret, defect and preference deadlines for a specific order, and whether the legal warranty still applies.
- **Store policies**: hours, contact, payment, shipping, returns, warranty and privacy.
- **Open now**: uses the store timezone and business hours.
- **Out of scope**: refuses accessories, since the store sells instruments only, and unrelated topics.
- **Handoff**: registers a case for the team with a protocol number when the agent cannot solve it.
- **Tests**: 263 automated tests without LLM calls, plus 19 manual conversations against the real model, including prompt injection and multi turn memory.

## Technical decisions

- **One agent with tool calling.** Questions mix domains, such as a return needing both the order and the policy. A token cost estimate for a 7 message conversation put one agent with the manual behind a tool at about US$ 0.031, a router with specialists at US$ 0.033 and a supervisor with subagents at US$ 0.047. With only 7 tools, splitting adds routing calls and latency with no saving.
- **Policies through a tool instead of vector RAG.** The manual has 8 pages split into clear sections, so the model picks the section it needs and gets the exact text. Vector RAG would add an embedding model, a vector store and chunking for a document this small, with less precise results. Keeping the manual out of the system prompt also cut about 24% of the tokens in the same estimate.
- **`google/gemini-3.8-flash` via OpenRouter.** A reliable model with solid tool calling at low cost and latency, which suits a support chat. OpenRouter makes switching models a one variable change.
- **Short system prompt with global rules**, such as never stating prices or policies without a tool result and verifying before talking about an order. Tool specific instructions live in each tool description, so the model reads them only where they apply.
- **Reference date set to 2026-03-25.** The data ends in March 2026, so with the real date every return deadline would be expired and every pending order would look months late. Simulating today keeps the data exactly as delivered. Leaving it empty uses the real date.
- **History in memory, trimmed to the last 6 turns.** A support session only needs the current conversation, and trimming keeps token usage stable.
- **Challenge data versioned in the repository**, so the project runs with the store data right after cloning. This is a choice for the challenge only; with a real client the data would come from the store systems and would never be committed.
- **HTTP API with a simple UI**, so any channel such as web or WhatsApp can use the same agent. The UI exists for testing and demo.

## Data handling and assumptions

The CSVs live unchanged in `back-end/seed/csv/`, the manual is transcribed by section in `back-end/seed/policies/`, and `scripts/seed_db.py` loads both into the database.

- **Contact**: the manual has two phone numbers and an email with an accented domain. The transcription uses (67) 3341-4444, from the official company data table, and the email without accent.
- **Installments**: the payment table and section 3.1 disagree on the minimum installment. Section 3.1 prevails as the more specific rule.
- **Receipt date**: deadlines count from receipt, but orders only have `estimated_delivery`, which is used as the receipt date, and the agent presents deadlines as estimates.
- **Regret right**: the manual grants it for online purchases only, but orders have no channel field. All orders are treated as online, since they have tracking codes.
- **Product status** is the source of truth: `discontinued` and `coming_soon` products are never offered as available, even with stock.
- **Products 135 to 144**: seven of them have a description of another product, such as "Music Man Bass 1X" described as a Fender Jazz Bass. Their descriptions are dropped on load, listed in `back-end/seed/corrections.toml`, and the agent relies on name and specs.

## Known limitations

- English category names like "acoustic guitars" miss on the first search because the data is in Portuguese. The agent recovers with the category list returned by the tool, at the cost of one extra call.
- Conversation history is lost on restart and is not shared between processes.
- Search returns at most 10 products.
- Holidays are not configured, so the store may be reported as open on a holiday.
- Replies use markdown, which WhatsApp does not render the same way.
- No authentication or rate limiting.

## Next steps

- Automated evals with the LLM, checking which tools were called and which facts appear in the answer, also used to compare models.
- Persistent conversation history with a Postgres or Redis checkpointer.
- Pagination in product search.
- Confirm the correct descriptions of products 135 to 144 with the store.
- Channel specific formatting for WhatsApp.
- Migrations with Alembic, CI, and async LLM calls for higher concurrency.

## AI assisted workflow

**Claude Code** was used throughout the project:

- **Planning and development** with spec driven development: analysis of the challenge, manual and data, a decisions log, tool specs, architecture cost simulation and a test plan written before any code, then implementation in small steps with tests alongside, with every change reviewed manually.
- **Large scale testing** through the chat: Claude ran the test scenarios against the API and logged answers, tool calls, tokens and cost. Based on these results and the conversation history, prompts and tools were optimized and fixed.

## Running the project

Docker is the simplest option. Running locally requires Python 3.14 and Node 24.

### With Docker

```bash
cp .env.example .env
cp back-end/.env.example back-end/.env   # set OPENROUTER_API_KEY
docker compose up --build
```

The store data is loaded on the first start.

- Chat UI: http://localhost:8080
- API docs: http://localhost:8000/docs

### Locally

Backend:

```bash
cd back-end
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows PowerShell; use source .venv/bin/activate on Linux/macOS
pip install -r requirements-dev.txt
cp .env.example .env          # set OPENROUTER_API_KEY
python -m scripts.seed_db
uvicorn app.main:create_app --factory --reload
```

Frontend:

```bash
cd front-end
cp .env.example .env
npm install
npm run dev                   # http://localhost:5173
```

Tests:

```bash
cd back-end
pytest
```
