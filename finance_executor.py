"""A2A SDK executor for deterministic purchase-order validation."""

import json

from a2a.helpers import get_message_text, new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState
from pydantic import BaseModel, Field, ValidationError


class InvoiceCheck(BaseModel):
    invoice_id: str = Field(min_length=1)
    vendor: str = Field(min_length=1)
    amount: float = Field(gt=0)
    purchase_order_total: float = Field(gt=0)


class FinanceAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task_from_user_message(context.message)
        if context.current_task is None:
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.update_status(
            state=TaskState.TASK_STATE_WORKING,
            message=new_text_message("Checking invoice against purchase order."),
        )

        try:
            raw = get_message_text(context.message)
            invoice = InvoiceCheck.model_validate(json.loads(raw))
            if invoice.amount <= invoice.purchase_order_total:
                result = f"APPROVE: {invoice.invoice_id} is within the purchase order amount."
            else:
                result = f"REVIEW: {invoice.invoice_id} exceeds the purchase order amount."
        except (json.JSONDecodeError, ValidationError, TypeError) as exc:
            result = f"REVIEW: Invalid invoice payload ({exc})."

        await updater.add_artifact(parts=[new_text_part(text=result, media_type="text/plain")])
        await updater.update_status(
            state=TaskState.TASK_STATE_COMPLETED,
            message=new_text_message("Invoice check completed."),
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Cancellation is not supported by this demo.")
