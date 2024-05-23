import requests

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
            print(e)

        # Finds the number of notes
        results_json = response.json()
        page_items = len(results_json["items"])
        page = 0
        while page_items > 99:
            new_url = f"{url}&order_by=updated_time&page={page}"
            response = requests.get(new_url)
            results_json = response.json()
            page_items = len(results_json["items"])
            page = page + 1

        total_notes = (100 * (page - 1) + page_items)
        latest_updated = results_json["items"][page_items - 1]
        server_alive = self.get_server_status()

        print(f"\npages: {page}\ntotal notes: {total_notes}\nlatest updated: {latest_updated['title']}\nserver alive: {server_alive}\n")

        # TODO: Get all folders (and remove the "Week 1" ones)

        # TODO: Get all images (resources)

        # TODO: Get all tags

if __name__ == "__main__":
    server_url = "http://192.168.1.20:1012/joplin-cache"

    ja = JoplinApi()
    ja.retrieve_notes()
    # requests.put(server_url, ja.retrieve_notes)
