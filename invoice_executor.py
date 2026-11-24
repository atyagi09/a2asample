"""A2A SDK executor that delegates invoice validation to the Finance Agent."""

import json
import os

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import get_message_text, new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Role, SendMessageRequest, TaskState
from pydantic import BaseModel, Field, ValidationError


class Invoice(BaseModel):
    invoice_id: str = Field(min_length=1)
    vendor: str = Field(min_length=1)
    amount: float = Field(gt=0)
    purchase_order_total: float = Field(gt=0)


class InvoiceAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task_from_user_message(context.message)
        if context.current_task is None:
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.update_status(
            state=TaskState.TASK_STATE_WORKING,
            message=new_text_message("Discovering Finance Agent and delegating validation."),
        )

        try:
            invoice = Invoice.model_validate(json.loads(get_message_text(context.message)))
            finance_url = os.getenv("FINANCE_AGENT_URL", "http://127.0.0.1:8001")
            async with httpx.AsyncClient(timeout=15) as http_client:
                resolver = A2ACardResolver(httpx_client=http_client, base_url=finance_url)
                finance_card = await resolver.get_agent_card()
                finance_client = await create_client(
                    agent=finance_card,
                    client_config=ClientConfig(streaming=False),
                )
                try:
                    message = new_text_message(invoice.model_dump_json(), role=Role.ROLE_USER)
                    request = SendMessageRequest(message=message)
                    replies = [str(reply) async for reply in finance_client.send_message(request)]
                finally:
                    await finance_client.close()
            result = f"Delegated to {finance_card.name}. Finance Agent response: {' '.join(replies)}"
        except (json.JSONDecodeError, ValidationError, TypeError, httpx.HTTPError, ValueError) as exc:
            result = f"Could not complete invoice validation: {exc}"

        await updater.add_artifact(parts=[new_text_part(text=result, media_type="text/plain")])
        await updater.update_status(
            state=TaskState.TASK_STATE_COMPLETED,
            message=new_text_message("Invoice processing completed."),
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Cancellation is not supported by this demo.")
