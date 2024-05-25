"""Get the status of Joplin notes from the laptop and send them to the Rocky server."""
import time
import requests

class JoplinApi:  # pylint: disable=too-few-public-methods
    """Uses the Joplin API to retrieve details about the Joplin instance."""
    def __init__(self):
        self.token = "badc14eee6bd7985cd26767a1ae5351294a186a5ca06f0ea2cb46a8e38967e574c61ee5dbbd47038644c5719d9acb86ac008f22ae2fc820ff2badb4ff3db565d"
        self.url_root = "http://localhost:41184/"
        self.server_url = "https://joplin.hj320mcserver.xyz/"

    def get_server_status(self) -> bool:
        """Return whether or not the server is alive.

        Returns:
            bool: True if server is online.
        """
        try:
            status_response = requests.get(f"{self.server_url}/api/ping", timeout=5)
            status_response.raise_for_status()
        except requests.exceptions.HTTPError as status_error:
            print(status_error)
            return False

        response_json = status_response.json()

        if response_json["status"] == "ok":
            return True
        return False



    def retrieve_notes(self) -> dict:
        """Makes requests to the Joplin API to get the number of: notes, images, folders, etc.

        Returns:
            dict: Dict containing the details from the Joplin API, or errors encountered.
        """
        # pylint: disable=too-many-locals

        # For loop to request the URL until retrieving one where the size isn't 100
        url = f"{self.url_root}notes?token={self.token}"
        # response = requests.get()

        # Check that the Joplin API is alive.
        try:
            notes_response = requests.get(url, timeout=5)
            notes_response.raise_for_status()
        except requests.exceptions.HTTPError as notes_error:
            return {
                # "pages": 0,
                # "notes": 0,
                # "newest": "",
                # "images": 0,
                # "folders": 0,
                # "tags": 0,
                "server_alive": self.get_server_status(),
                "joplin_running": False,
                "error": notes_error
            }
        # Entered if Joplin is closed.
        except requests.exceptions.ConnectionError as notes_error:
            return {
                "server_alive": self.get_server_status(),
                "joplin_running": False,
                "error": notes_error
            }


        # Finds the number of notes.
        page_items = 100
        page = 0
        while page_items > 99:
            new_url = f"{url}&order_by=updated_time&page={page}"
            specific_page_response = requests.get(new_url, timeout=5)
            results_json = specific_page_response.json()
            page_items = len(results_json["items"])
            page = page + 1

        total_notes = 100 * (page - 1) + page_items
        server_alive = self.get_server_status()
        latest_updated = results_json["items"][page_items - 1]
        note_pages = page


        # Gets all images (resources).
        images_url = f"{self.url_root}resources?token={self.token}"
        images_response = requests.get(images_url, timeout=5).json()["items"]
        total_images = len(images_response)

        # Gets all folders (and removes the "Week 1" ones).
        folders_url = f"{self.url_root}folders?token={self.token}"
        folders = set()
        page_items = 100
        page = 0
        while page_items > 99:
            new_url = f"{folders_url}&order_by=updated_time&page={page}"
            folders_response = requests.get(new_url, timeout=5).json()["items"]
            page_items = len(folders_response)
            for folder_dict in folders_response:
                if "Week" not in folder_dict["title"]:
                    folders.add(folder_dict["title"])
            page = page + 1

        # print(f"Folders: {len(folders)}")


        # Gets all tags.
        tags_url = f"{self.url_root}tags?token={self.token}"
        tags = set()
        page_items = 100
        page = 0
        while page_items > 99:
            new_url = f"{tags_url}&order_by=updated_time&page={page}"
            tags_response = requests.get(new_url, timeout=5).json()["items"]
            page_items = len(tags_response)
            for tags_dict in tags_response:
                tags.add(tags_dict["title"])
            page = page + 1

        print(f"\npages: {note_pages}\ntotal notes: {total_notes}\nlatest updated: {latest_updated['title']}\nimages: {total_images}")
        print(f"folders: {len(folders)}\ntags: {len(tags)}\nserver alive: {server_alive}\n")

        output = {
            "pages": note_pages,
            "notes": total_notes,
            "newest": latest_updated["title"],
            "images": total_images,
            "folders": len(folders),
            "tags": len(tags),
            "server_alive": server_alive,
            "joplin_running": True,
            "error": "",
            "time": time.time()
        }

        return output

if __name__ == "__main__":
    # server_url = "http://127.0.0.1:1012/joplin-cache"
    SERVER_URL = "http://192.168.1.20:1012/joplin-cache"


    ja = JoplinApi()
    try:

        note_details = ja.retrieve_notes()
        # note_details_json = json.dumps(note_details)
        response = requests.put(SERVER_URL, timeout=10, json=note_details)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)

    print(response.json())
