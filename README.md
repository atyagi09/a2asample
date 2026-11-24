# A2A Invoice Processing Demo

Two independent A2A 1.0 agents implemented with the official Python SDK. The Invoice Agent discovers the Finance Agent through its Agent Card and delegates purchase-order validation through the SDK client over JSON-RPC. Both expose Agent Cards and SDK request handlers. The validation is deterministic and requires no model API key.

## Run locally

Requires Python 3.10+.

```powershell
cd outputs/a2a-invoice-demo
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start Finance Agent in one terminal:

```powershell
python finance_agent.py
```

Start Invoice Agent in a second terminal:

```powershell
python invoice_agent.py
```

In a third terminal, call Invoice Agent through the official A2A client:

```powershell
python demo_client.py
```

The sample posts an invoice within the purchase-order limit. Edit the sample in `demo_client.py` to see the Finance Agent return a review recommendation for an over-limit invoice.

Agent Cards are available from each agent's standard discovery endpoint. The Finance Agent URL is `http://127.0.0.1:8001/.well-known/agent-card.json`; the Invoice Agent URL is `http://127.0.0.1:8000/.well-known/agent-card.json`.

The Finance Agent address can be changed with `FINANCE_AGENT_URL`. For deployment outside this local demo, set each Agent Card's advertised URL to its reachable HTTPS endpoint and configure the appropriate authentication and transport security.

## File map

- `finance_agent.py`: Finance Agent Card and SDK JSON-RPC server.
- `finance_executor.py`: Finance validation task executor.
- `invoice_agent.py`: Invoice Agent Card and SDK JSON-RPC server.
- `invoice_executor.py`: Invoice executor; discovers and calls Finance Agent.
- `demo_client.py`: SDK client that discovers and calls Invoice Agent.
- `requirements.txt`: pinned official A2A SDK plus runtime dependencies.

This uses the official A2A SDK rather than manually constructing protocol responses. It demonstrates the A2A 1.0 JSON-RPC transport; authentication, TLS termination, durable task storage, and production deployment configuration are environment-specific and intentionally left to the deployer.
