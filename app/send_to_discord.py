"""Module to use Discord webhooks to send a Discord message."""

import asyncio
import click
from discord import Webhook, errors
import aiohttp
# import requests
# from pydantic import BaseModel

async def send_discord_webhook(username: str, message: str, webhook_url: str) -> bool:
    """Generic function to send a Discord message to any Discord webhook.

    Args:
        username (str): Username that the message should appear to come from.
        message (str): Contents of the message sent.
        webhook_url (str): URL of the Discord webhook.

    Returns:
        bool: True if send was successful.
    """

    # webhook_url = 'https://discord.com/api/webhooks/1232449180471918624/8p8DZ6AP0Mp6xLwKKM3KaCN-seJhxTd0k8ge0F1smO2DLVX5HniNvyFV2oz2bcM3UmlA'
    try:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(webhook_url, session=session)
            await webhook.send(message, username=username)
        return True
    except errors.HTTPException:
        return False



@click.command()
@click.argument('username', type=str, metavar='<username>', nargs=1)
@click.argument('message', type=str, metavar='<message>', nargs=1)
@click.argument('webhook_url', type=str, metavar='<webhook_url>', nargs=1)
def main(username, message, webhook_url):
    """Send a message to a Discord webhook.

    Args:
        username (str): Username that the message should appear to come from.
        message (str): Contents of the message sent.
        webhook_url (str): URL of the Discord webhook.
    """
    result = asyncio.run(send_discord_webhook(username, message, webhook_url))
    print("Message sent:", result)

if __name__ == '__main__':
    URL = 'https://discord.com/api/webhooks/1232449180471918624/8p8DZ6AP0Mp6xLwKKM3KaCN-seJhxTd0k8ge0F1smO2DLVX5HniNvyFV2oz2bcM3UmlA'
    main()  # pylint: disable=no-value-for-parameter
