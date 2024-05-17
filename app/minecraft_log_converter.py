import os
from pathlib import Path
import shutil
import json
from datetime import datetime

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
        find_oldest = self.find_oldest()

        # Extracts the joined, left and banned info.
        
        # TODO: THIS IS ONLY SET FOR TESTING
        self.shortened_name = "minecraft-server-shortened.log"
        joined = self.extract_joined()

        # Extracts all Minecraft commands run.
        commands = self.extract_commands()


        # return f"Hey there champ! {joined}"
        # return joined
        # return commands
        return {"Hey": find_oldest}
    
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

        # Check if the joined.log file already exists.
        if Path(joined_log).is_file():

            # Finds the oldest entry in joined.log.
            joined_log = f"{self.log_location}{self.joined_name}"
            with open(joined_log) as joined:
                joined_first_line = joined.readline().strip('\n')
            
            # Get the oldest entry in joined.log
            oldest_joined = ""
            if joined_first_line != "":
                oldest_joined_time = joined_first_line.split(" ")[0]
                oldest_joined_time = oldest_joined_time.split(".")[0]
                oldest_joined = datetime.strptime(oldest_joined_time, '%Y-%m-%dT%H:%M:%S')

        # If there a commands.log file.
        if Path(commands_log).is_file():
            # Finds the oldest entry in joined.log.
            commands_log = f"{self.log_location}{self.joined_name}"
            with open(commands_log) as commands:
                commands_first_line = commands.readline().strip('\n')

            oldest_commands = ""
            if commands_first_line != "":
                # Get the oldest entry in joined.log
                oldest_commands_time = commands_first_line.split(" ")[0]
                oldest_commands_time = oldest_commands_time.split(".")[0]
                oldest_commands = datetime.strptime(oldest_commands_time, '%Y-%m-%dT%H:%M:%S')
        
        # Set oldest_log to whichever datetime is oldest.
        oldest_log = "Not existent"
        if oldest_joined != "" and oldest_commands != "":
            if oldest_joined > oldest_commands:
                oldest_log = oldest_commands
            else:
                oldest_log = oldest_joined


        
        # Copies the original log into a new folder
        self.shortened_name = "minecraft-server-shortened.log"
        shutil.copy2(original_log, f"{self.log_location}{self.shortened_name}")

        # Removes all entries older than that from self.shortened_name.
        # TODO: ACTUALLY JUST WRITE THE NEW FILES, DONT SHUTIL.COPY2

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

        # "[00:00:13 INFO]: \u001b[93mThe_4ngry_5quid joined the game\u001b[0m\r\n"
        # "[00:00:30 INFO]: The_4ngry_5quid issued server command: /time add 6000\r\n"


        shortened_log = f"{self.log_location}{self.shortened_name}"

        # Extract all lines into an array.
        with open(shortened_log) as short:
            lines = [line.rstrip() for line in short]

        keywords = ["joined ", "left ", "Banned "]

        matches = []
        for line in lines:
            if "issued server command" in line:
                json_object = json.loads(line)

                timestamp = json_object["time"]
                log = json_object["log"]

                # Removes starting and trailing characters.
                try:
                    username = log.split(": ")[1]
                    username = username.split(" ")[0]

                    command = log.split(": ")[2]
                    command = command.split("\r")[0]
                    # log_shortened = log_shortened.split("\x1b")[0]
                except IndexError as e:
                    # Catches if this is not  command log.
                    continue

                
                # 2024-05-13T09:18:54 Command The_4ngry_5quid "/gamemode survival"
                matches.append(f"{timestamp} command {username} '{command}'")

        commands_log = f"{self.log_location}{self.commands_name}"
        with open(commands_log, "a+") as commands:
            for match in matches:
                commands.write(match + "\n")

        return matches

        return
