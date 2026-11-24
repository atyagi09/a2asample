"""A2A SDK server exposing the Finance Agent over JSON-RPC."""

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette

from finance_executor import FinanceAgentExecutor

HOST = "127.0.0.1"
PORT = 8001

skill = AgentSkill(
    id="validate-invoice",
    name="Validate invoice",
    description="Compare an invoice amount with its purchase order total.",
    input_modes=["text/plain"],
    output_modes=["text/plain"],
    tags=["invoice", "finance", "purchase-order"],
    examples=['{"invoice_id":"INV-1042","vendor":"Northwind Supplies","amount":850,"purchase_order_total":1000}'],
)

agent_card = AgentCard(
    name="Finance Agent",
    description="Checks invoice totals against purchase order totals.",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            url=f"http://{HOST}:{PORT}",
            protocol_version="1.0",
        )
    ],
    skills=[skill],
)

request_handler = DefaultRequestHandler(
    agent_executor=FinanceAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)
app = Starlette(
    routes=[
        *create_agent_card_routes(agent_card),
        *create_jsonrpc_routes(request_handler, "/"),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
