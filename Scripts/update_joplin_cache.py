import requests
import json

class JoplinApi:  # pylint: disable=too-few-public-methods

    def __init__(self):
        self.token = "badc14eee6bd7985cd26767a1ae5351294a186a5ca06f0ea2cb46a8e38967e574c61ee5dbbd47038644c5719d9acb86ac008f22ae2fc820ff2badb4ff3db565d"
        self.url_root = "http://localhost:41184/"
        self.server_url = "https://joplin.hj320mcserver.xyz/"

    def get_server_status(self):
        try: 
            response = requests.get(f"{self.server_url}/api/ping")
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            return False
        
        response_json = response.json()

        if response_json["status"] == "ok":
            return True
        return False



    def retrieve_notes(self):

        # For loop to request the URL until retrieving one where the size isn't 100
        url = f"{self.url_root}notes?token={self.token}"
        # response = requests.get()

        # Check that the Joplin API is alive.
        try: 
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {
                # "pages": 0,
                # "notes": 0,
                # "newest": "",
                # "images": 0,
                # "folders": 0,
                # "tags": 0,
                "server_alive": self.get_server_status(),
                "joplin_running": False,
                "error": e
            }
        # Entered if Joplin is closed.
        except requests.exceptions.ConnectionError as e:
            return {
                "server_alive": self.get_server_status(),
                "joplin_running": False,
                "error": e
            }


        # Finds the number of notes.
        page_items = 100
        page = 0
        while page_items > 99:
            new_url = f"{url}&order_by=updated_time&page={page}"
            response = requests.get(new_url)
            results_json = response.json()
            page_items = len(results_json["items"])
            page = page + 1
        
        total_notes = (100 * (page - 1) + page_items)
        server_alive = self.get_server_status()
        latest_updated = results_json["items"][page_items - 1]
        note_pages = page


        # Gets all images (resources).
        images_url = f"{self.url_root}resources?token={self.token}"
        response = requests.get(images_url).json()["items"]
        total_images = len(response)

        # Gets all folders (and removes the "Week 1" ones).
        folders_url = f"{self.url_root}folders?token={self.token}"
        folders = set()
        page_items = 100
        page = 0
        while page_items > 99:
            new_url = f"{folders_url}&order_by=updated_time&page={page}"
            response = requests.get(new_url).json()["items"]
            page_items = len(response)
            for folder_dict in response:
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
            response = requests.get(new_url).json()["items"]
            page_items = len(response)
            for tags_dict in response:
                tags.add(tags_dict["title"])
            page = page + 1

        # TODO: Add last cache resync

        # TODO: Calculate total size.

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
            "error": ""
        }

        return output

if __name__ == "__main__":
    # server_url = "http://127.0.0.1:1012/joplin-cache"
    server_url = "http://192.168.1.20:1012/joplin-cache"


    ja = JoplinApi()
    try: 

        note_details = ja.retrieve_notes()
        # note_details_json = json.dumps(note_details)
        response = requests.put(server_url, json=note_details)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)

    print(response.json())
