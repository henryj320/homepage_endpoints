"""Gather details on directories in Rocky Share."""

from datetime import datetime
import json
import os
import time
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from discord import Webhook
import aiohttp
import requests

def update_filestore():
    """Updates the filestore cache on a schedule."""
    cache_file_location = "../cache/filestore.json"

    # Get the majority of directory details.
    directory = "/sharedFolder"
    details = get_details(directory)

    # Get the number of users.
    items = os.listdir(directory)
    folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]
    users = len(folders)

    to_dict = {
        "files": details["images"],
        "last_mod": details["last_sync"],
        "total_size": details["total_size"],
        "users": users,
        "added_this_week": details["synced_this_week"],
    }

    # Convert to JSON and dump into filestore.json.
    dict_to_json = json.dumps(to_dict, indent=4)
    with open(cache_file_location, "w", encoding="utf-8") as file:
        file.write(dict_to_json)


# Runs update_filestore() every.
scheduler = BackgroundScheduler()
scheduler.add_job(update_filestore, "interval", minutes=30)
scheduler.start()

app = FastAPI()


@app.get("/Henry")
def get_henry_details() -> dict:
    """Get details on the images synced from Henry's phone to the server.

    Returns:
        dict: The number of images, last sync date, total size and images synced this week.
    """
    directory = "/upload/Henry"
    return get_details(directory)


@app.get("/Poppy")
def get_poppy_details() -> dict:
    """Get details on the images synced from Poppy's phone to the server.

    Returns:
        dict: The number of images, last sync date, total size and images synced this week.
    """
    directory = "/upload/Poppy"
    return get_details(directory)


@app.get("/filestore")
def get_filestore_details() -> dict:
    """Return details on the files stored on the Samba.

    Returns:
        dict: The number of files, last modification, total size and number of users.
    """
    location = "/cache/filestore.json"

    # Set up the filestore if it is empty.
    if os.path.getsize(location) < 1:
        update_filestore()

    # Read and return the content of the cache file.
    with open(location, "r", encoding="utf-8") as json_file:
        loaded_data = json.load(json_file)
    return loaded_data


@app.get("/update-ip")
async def update_ip_to_discord() -> dict:
    """Check the Current IP and send new public IPs to discord. Cronjob to curl this every 30 minutes.

    Returns:
        dict: Status of the public IP.
    """

    cache_file_location = "../cache/ips.txt"

    # Read the cache file for the latest IP.
    last_ip = ''
    with open(cache_file_location, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if lines:
            last_ip = lines[-1].strip()
        else:
            last_ip = ''

    # Check when the public IP last changed.
    mtime = os.path.getmtime(cache_file_location)
    last_update = datetime.fromtimestamp(mtime).strftime("%d %B")
    last_run = datetime.fromtimestamp(time.time()).strftime("%d %B at %H:%M")


    # Get the current public IP.
    public_ip = ""
    try:
        response = requests.get('https://ipinfo.io/ip', timeout=30)
        response.raise_for_status()  # Raises an exception for 4XX or 5XX errors
        public_ip = response.text
    except requests.RequestException as e:
        output = {
            "status": f"Error retrieving IP: {e}",
            "ip": public_ip,
            "last_update": last_update,
            "last_run": last_run
        }
        return output
    
    # If IP has not changed.
    if last_ip == public_ip:
        output = {
            "status": "Same IP",
            "ip": public_ip,
            "last_update": last_update,
            "last_run": last_run
        }
        return output

    # If IP has changed.
    with open(cache_file_location, 'a', encoding='utf-8') as file:
        file.write(public_ip + '\n')

    webhook_url = 'https://discord.com/api/webhooks/1232449180471918624/8p8DZ6AP0Mp6xLwKKM3KaCN-seJhxTd0k8ge0F1smO2DLVX5HniNvyFV2oz2bcM3UmlA'
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        await webhook.send(f"Public IP changed to: {public_ip}", username='Public IP Checker')

    last_update = datetime.fromtimestamp(time.time()).strftime("%d %B")

    output = {
        "status": "IP Changed",
        "ip": public_ip,
        "last_update": last_update,
        "last_run": last_run
    }
    return output


def get_details(directory: str) -> dict:
    """Returns details on the files inside the directory.

    Args:
        directory (str): Directory to check.

    Returns:
        dict: Details on the directory.
    """
    # Get the total number of files.
    latest_mtime = 0
    total_size = 0

    unique_files = set()
    modified_this_week = set()

    for root, dirs, files in os.walk(directory):
        #  Get when the most recent is updated.
        for file in files:
            file_path = os.path.join(root, file)
            mtime = os.path.getmtime(file_path)
            if mtime > latest_mtime:
                latest_mtime = mtime

            # Calculate the difference in seconds between now and the modification time
            time_difference = time.time() - mtime
            days_difference = time_difference / (60 * 60 * 24)
            if days_difference < 7:
                modified_this_week.add(file_path)

            # Combine sizes together to get the total size
            total_size += os.path.getsize(file_path)

            # Catch because of the hidden ".thumbnail" directory
            if ".thumbnail" not in file_path:
                unique_files.add(file_path)

    # total_size = os.path.getsize(directory)
    total_size = round(total_size / (1024**3), 2)

    # seconds_since_update = time.time() - latest_mtime
    # last_update = datetime.fromtimestamp(latest_mtime).strftime('%d %B at %H:%M')
    last_update = datetime.fromtimestamp(latest_mtime).strftime("%d %B")

    # Adds commas to the number
    num_of_images = f"{len(unique_files):,}"

    to_dict = {
        "images": num_of_images,
        "last_sync": last_update,
        "total_size": total_size,
        "synced_this_week": len(modified_this_week),
    }

    return to_dict


# docker compose up -d --force-recreate --build
# docker exec -it clamav_homepage sh
# docker logs clamav_homepage
# pylint --max-line-length=240 ./main.py
