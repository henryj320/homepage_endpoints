import asyncio
from discord import Webhook
import aiohttp
# import requests
# from pydantic import BaseModel

async def send_discord_webhook(username: str, message: str, webhook_url: str):
    """Generic function to send a Discord message to any Discord webhook

    Args:
        username (str): Username that the message should appear to come from.
        message (str): Contents of the message sent.
        webhook_url (str): URL of the Discord webhook.

    Returns:
        _type_: _description_
    """

    # webhook_url = 'https://discord.com/api/webhooks/1232449180471918624/8p8DZ6AP0Mp6xLwKKM3KaCN-seJhxTd0k8ge0F1smO2DLVX5HniNvyFV2oz2bcM3UmlA'
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        await webhook.send(message, username=username)

    return True

if __name__ == '__main__':
    webhook_url = 'https://discord.com/api/webhooks/1232449180471918624/8p8DZ6AP0Mp6xLwKKM3KaCN-seJhxTd0k8ge0F1smO2DLVX5HniNvyFV2oz2bcM3UmlA'

    result = asyncio.run(send_discord_webhook("Test Username", "This is a message", webhook_url))
    print(result)

