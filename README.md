## Astrologer MCP Server / Puch AI

AI-powered Vedic astrology over the Model Context Protocol (MCP). The server accepts birth details, persists user profiles (via n8n + Qdrant), and generates answers with OpenAI. It exposes MCP tools over a streamable HTTP endpoint and is deployable as a Render Web Service and built for Puch AI.

### Features

- AI-generated astrological insights with OpenAI
- Persistent user memory via n8n → Qdrant (with in-memory fallback)
- Bearer-token authentication for MCP requests
- FastAPI app with health endpoints and MCP mounted at `/mcp/`
- Ready-to-deploy Render configuration (Python web service)
- Startup OpenAI API key validation and structured logging

### Architecture

```
Client (MCP Host) → MCP Server (/mcp) → n8n (webhook) → Qdrant
                               ↘︎ OpenAI (insights)
```

## Requirements

- Python 3.11+
- OpenAI API key
- Optional: n8n webhook + Qdrant cluster for persistent memory

## Quick Start (Local)

1) Install dependencies
```bash
pip install -r requirements.txt
```

2) Create `.env` in the project root
```env
AUTH_TOKEN=your_bearer_token
MY_NUMBER=your_phone_number
OPENAI_API_KEY=your_openai_api_key
N8N_WEBHOOK_URL=https://your-n8n/webhook/astrologer-storage
N8N_WEBHOOK_SECRET=your_webhook_secret
```

3) Run the server
```bash
python mcp-bearer-token/puch_astro_mcp.py
```

Health checks:
- `GET http://localhost:8086/` → basic status
- `GET http://localhost:8086/health` → detailed status

MCP endpoint:
- `http://localhost:8086/mcp/` (requires SSE and session headers; use an MCP host/client)

## Tool Reference

### validate
- Returns the configured phone number (string) used by clients for validation.

### astro_register_profile
Registers birth details and stores the profile.
- Inputs: `name` (str), `dob` (YYYY-MM-DD), `time` (HH:mm, 24h), `place` (str), `session_id` (optional str)
- Output: Text content with profile summary and initial insights

### astro_ask
Answers a question using profile data. If birth details are provided and no `profile_id`, a profile is created automatically.
- Inputs: `question` (str), `name?` (str), `dob?` (YYYY-MM-DD), `time?` (HH:mm), `place?` (str), `timeframe?` (str), `profile_id?` (str)
- Output: Text content with insights (and profile creation note if applicable)

## Using with Puch AI (MCP)

Puch AI supports connecting to external MCP servers over HTTPS and requires a validate tool.

- The validate tool must return the server owner's phone number as digits only: {country_code}{number}
  - Example: `919337015103` for +91-9337015103
- Ensure your server is publicly accessible (e.g., Render deployment)

### Connect (Bearer Token)

In any Puch conversation, run:

```text
/mcp connect https://your-app.onrender.com/mcp/ astrology
```

After connecting, Puch will validate and then list available tools (validate, astro_register_profile, astro_ask).

### Useful Commands

- List connected servers:
  - `/mcp list`
- Disconnect all MCP servers:
  - `/mcp deactivate`
- Set diagnostics verbosity:
  - `/mcp diagnostics-level info` (options: error|warn|info|debug)

If you use a hosted MCP server provided by Puch:
- `/mcp use <server_id>` to enable
- `/mcp remove <server_id>` to remove

### Requirements Recap

- HTTPS endpoint (Render deploy recommended)
- Bearer token: set `AUTH_TOKEN` (example: `astrology`)
- Phone number: set `MY_NUMBER` as digits only (e.g., `919337015103`)

### Other MCP Hosts (JSON)

If your host uses a JSON config instead of chat commands:

```json
{
  "mcpServers": {
    "astrologer": {
      "url": "https://your-app.onrender.com/mcp/",
      "auth": { "type": "bearer", "token": "astrology" }
    }
  }
}
```

## Deployment (Render)

This repo includes a Python-first Render setup:
- `render.yaml`
- `render_start.py` (starts the FastAPI app)
- `requirements.txt`

Follow the detailed instructions in `RENDER_DEPLOYMENT.md`.

## Security & Logging

- Authentication: Bearer token (`AUTH_TOKEN`)
- HTTPS is required in production
- Logs: written to `mcp_server.log` (UTF‑8). On startup, the server validates the OpenAI key and reports status. The key is not printed in full.

## Troubleshooting

- OpenAI 401/invalid key: ensure `OPENAI_API_KEY` is set in the environment where the process runs (Render dashboard, not `.env`).
- MCP requests via curl fail: MCP requires `Accept: text/event-stream` and a session; use an MCP host (e.g., Puch AI) instead of raw curl.
- n8n/Qdrant not reachable: the server falls back to in-memory storage for profiles.
- Wrong token: verify the MCP client is sending `Authorization: Bearer <AUTH_TOKEN>`.
- Python version: use 3.11 as configured for Render.

## Project Structure

```
.
├─ mcp-bearer-token/
│  └─ puch-astro-mcp.py        # MCP server (FastMCP + FastAPI)
├─ render.yaml                 # Render configuration (Python web service)
├─ render_start.py             # Render entry – starts FastAPI app
├─ requirements.txt            # Python dependencies
├─ RENDER_DEPLOYMENT.md        # Deployment guide
└─ README.md                   # This file
```

## License

MIT License. See `LICENSE`.
