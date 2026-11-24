"""Submit an invoice to the Invoice Agent using the official A2A client."""

import asyncio
import json

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import new_text_message
from a2a.types import Role, SendMessageRequest


async def main() -> None:
    invoice = {
        "invoice_id": "INV-1042",
        "vendor": "Northwind Supplies",
        "amount": 850,
        "purchase_order_total": 1000,
    }
    async with httpx.AsyncClient() as http_client:
        resolver = A2ACardResolver(httpx_client=http_client, base_url="http://127.0.0.1:8000")
        card = await resolver.get_agent_card()
        client = await create_client(agent=card, client_config=ClientConfig(streaming=False))
        try:
            message = new_text_message(json.dumps(invoice), role=Role.ROLE_USER)
            request = SendMessageRequest(message=message)
            async for response in client.send_message(request):
                print(response)
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
