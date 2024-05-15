import os
from pathlib import Path
import shutil
import json

class MinecraftLogConverter:  # pylint: disable=too-few-public-methods

    def __init__(self):

        self.log_location = "/sharedFolder/Henry/Logs/Minecraft/"
        self.original_name = "minecraft-server.log"
        self.joined_name = "joined.log"
        self.commands_name = "commands.log"
        self.shortened_name = ""

    def run(self):

        log = f"{self.log_location}{self.original_name}"
        size = os.path.getsize(log)

        # Finds the oldest logs already converted and removes any older than that.
        # find_oldest = self.find_oldest()

        # Extracts the joined, left and banned info.
        
        # TODO: THIS IS ONLY SET FOR TESTING
        self.shortened_name = "minecraft-server-shortened.log"
        joined = self.extract_joined()

        # Extracts all Minecraft commands run.
        # commands = self.extract_commands()


        # return f"Hey there champ! {joined}"
        return joined
    
    # joined.log
        # Joined, left, banned
        # 2024-05-13T01:46:26 Joined The_4ngry_5quid a05359ac-f1c9-4eb3-8943-6867a20b012c
    # commands.json
        # Commands run
        # 2024-05-13T09:18:54 Command The_4ngry_5quid "/gamemode survival"


    def find_oldest(self):
        # TODO: Find the oldest logs in the existing files and remove any that are older than that.

        original_log = f"{self.log_location}{self.original_name}"
        joined_log = f"{self.log_location}{self.joined_name}"
        commands_log = f"{self.log_location}{self.commands_name}"

        # Check if the files already exist.
        missing = False
        if not Path(joined_log).is_file():
            missing = True
        elif not Path(commands_log).is_file():
            missing = True
        
        # Copies the original log into a new folder
        self.shortened_name = "minecraft-server-shortened.log"
        shutil.copy2(original_log, f"{self.log_location}{self.shortened_name}")

        # Finds the oldest entry in joined.log.

        # Finds the oldest entry in commands.log.

        # Uses whichever is older.

        # Removes all entries older than that from self.shortened_name.

        return True


    def remove_old_logs(self, older_than: str):
        # TODO: Remove any unnecessary logs.
        return

    def extract_joined(self):
        # TODO: Extract the joined.log logs.
        shortened_log = f"{self.log_location}{self.shortened_name}"

        # Extract all lines into an array.
        with open(shortened_log) as short:
            lines = [line.rstrip() for line in short]

        keywords = ["joined ", "left ", "Banned "]

        matches = []
        for line in lines:
            if [line for keyword in keywords if(keyword in line)]:
                json_object = json.loads(line)

                timestamp = json_object["time"]
                log = json_object["log"]

                # Removes starting and trailing characters.
                try:
                    log_shortened = log.split("[93m")[1]
                    log_shortened = log_shortened.split("\x1b")[0]
                except IndexError as e:
                    # Catches if this is not joined/left/banned log.
                    continue

                # Special case for banned, as the format in logs is different.
                if "Banned" in log:
                    username = log_shortened.split(" ")[2]
                    matches.append(f"{timestamp} Banned")
                    continue

                for keyword in keywords:
                    username = log_shortened.split(" ")[0]
                    if keyword in log_shortened:
                        matches.append(f"{timestamp} {keyword}{username}")

        joined_log = f"{self.log_location}{self.joined_name}"
        with open(joined_log, "a+") as joined:
            for match in matches:
                joined.write(match + "\n")

        return matches


    def extract_commands(self):
        # TODO: Extract the commands.json logs.
        return
