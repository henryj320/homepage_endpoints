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
        self.shortened_name = "minecraft-server-shortened.log"

    def run(self):

        log = f"{self.log_location}{self.original_name}"
        size = os.path.getsize(log)

        # Extracts the joined, left and banned info.
        
        # TODO: THIS IS ONLY SET FOR TESTING
        # self.shortened_name = "minecraft-server-shortened.log"


        shortened_log = f"{self.log_location}{self.shortened_name}"
        if Path(shortened_log).is_file():
            os.remove(shortened_log)

        # If there are newer logs in joined.log that need to be added to shortened.log
        joined = self.extract_joined()
        updated = False
        if self.logs_are_newer(joined):
            with open(shortened_log, "a+") as short:
                for match in joined:
                    short.write(match + "\n")
            updated = True
        
        # Extracts all Minecraft commands run.
        commands = self.extract_commands()
        if self.logs_are_newer(commands):
            with open(shortened_log, "a+") as short:
                for match in commands:
                    short.write(match + "\n")
            updated = True

            # joined_logs_are_newer = 

        # return f"Hey there champ! {joined}"
        # return joined
        # return commands
        return {f"{self.log_location}{self.shortened_name} updated": updated}
    
    # joined.log
        # Joined, left, banned
        # 2024-05-13T01:46:26 Joined The_4ngry_5quid a05359ac-f1c9-4eb3-8943-6867a20b012c
    # commands.json
        # Commands run
        # 2024-05-13T09:18:54 Command The_4ngry_5quid "/gamemode survival"


    def logs_are_newer(self, logs_to_add: list):
        """Returns whether or not the logs_to_add are newer than the logs in shortened_name.

        Args:
            logs_to_add (list): _description_

        Returns:
            _type_: _description_
        """
        if logs_to_add == []:
            return False


        # TODO: Only update the 3x log files if the entry is newer than the newest
        # Find newest in log
        # If oldest is newer, then add all
            # Else, only add those that are newer
        
        # Get the line of the oldest log.
        try:
            shortened_log = f"{self.log_location}{self.shortened_name}"
            with open(shortened_log) as short:
                # shortened_first_line = short.readline().strip('\n')
                lines = short.readlines()
                newest_in_shortened = lines[-1]
        except FileNotFoundError as e:
            return True
        
        newest_in_logs_to_add = logs_to_add[-1]

        # If the logs to add are older than the existing logs in shortened_log (nothing to add)
        if self.get_date_from_string(newest_in_shortened) > self.get_date_from_string(newest_in_logs_to_add):
            print(newest_in_shortened)
            print(newest_in_logs_to_add)
            return False
        
        # If the logs to add are newer than the existing logs in shortened_log, so must be added
        # return f"{newest_in_shortened} - {newest_in_logs_to_add}"
        return True

        # # Get the line of the newest joined log.
        # joined_log = f"{self.log_location}{self.joined_name}"
        # with open(joined_log) as joined:
        #     # shortened_first_line = short.readline().strip('\n')
        #     lines = short.readlines()
        #     newest_in_shortened = lines[-1]



        # original_log = f"{self.log_location}{self.original_name}"
        # joined_log = f"{self.log_location}{self.joined_name}"
        # commands_log = f"{self.log_location}{self.commands_name}"

        # # Check if the joined.log file already exists.
        # if Path(joined_log).is_file():

        #     # Finds the oldest entry in joined.log.
        #     joined_log = f"{self.log_location}{self.joined_name}"
        #     with open(joined_log) as joined:
        #         joined_first_line = joined.readline().strip('\n')
            
        #     # Get the oldest entry in joined.log
        #     oldest_joined = ""
        #     if joined_first_line != "":
        #         oldest_joined_time = joined_first_line.split(" ")[0]
        #         oldest_joined_time = oldest_joined_time.split(".")[0]
        #         oldest_joined = datetime.strptime(oldest_joined_time, '%Y-%m-%dT%H:%M:%S')

        # # If there a commands.log file.
        # if Path(commands_log).is_file():
        #     # Finds the oldest entry in joined.log.
        #     commands_log = f"{self.log_location}{self.joined_name}"
        #     with open(commands_log) as commands:
        #         commands_first_line = commands.readline().strip('\n')

        #     oldest_commands = ""
        #     if commands_first_line != "":
        #         # Get the oldest entry in joined.log
        #         oldest_commands_time = commands_first_line.split(" ")[0]
        #         oldest_commands_time = oldest_commands_time.split(".")[0]
        #         oldest_commands = datetime.strptime(oldest_commands_time, '%Y-%m-%dT%H:%M:%S')
        
        # # Set oldest_log to whichever datetime is oldest.
        # oldest_log = "Not existent"
        # if oldest_joined != "" and oldest_commands != "":
        #     if oldest_joined > oldest_commands:
        #         oldest_log = oldest_commands
        #     else:
        #         oldest_log = oldest_joined


        
        # Copies the original log into a new folder
        # self.shortened_name = "minecraft-server-shortened.log"
        # shutil.copy2(original_log, f"{self.log_location}{self.shortened_name}")

        # Removes all entries older than that from self.shortened_name.

        return True


    def get_date_from_string(self, line: str) -> datetime:
        """Returns

        Args:
            line (str): Log line in the structure of "2024-05-16T11:32:08.835486479Z left Giddle".

        Returns:
            datetime: _description_
        """
        try:
            date_string = line.split(" ")[0]
            date_string = date_string.split(".")[0]

            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')

        except ValueError as e:
            return datetime.strptime("1999-01-01T01:01:01", '%Y-%m-%dT%H:%M:%S')


    def extract_joined(self):
        # TODO: Extract the joined.log logs.
        original_log = f"{self.log_location}{self.original_name}"

        # Extract all lines into an array.
        with open(original_log) as short:
            lines = [line.rstrip() for line in short]

        # If the joined logs are already added to shortened.log
        joined_log = f"{self.log_location}{self.joined_name}"
        if Path(joined_log).is_file():
            if not self.logs_are_newer(lines):
                return []


        keywords = ["joined ", "left ", "Banned "]

        matches = []
        raw = []
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
                    raw.append(line)
                    matches.append(f"{timestamp} Banned")
                    continue

                for keyword in keywords:
                    username = log_shortened.split(" ")[0]
                    if keyword in log_shortened:
                        raw.append(line)
                        matches.append(f"{timestamp} {keyword}{username}")

        

        # TODO: Only add if newer than the current logs!
        with open(joined_log, "a+") as joined:
            for match in matches:
                joined.write(match + "\n")

        shortened_log = f"{self.log_location}{self.shortened_name}"
        with open(shortened_log, "a+") as short:
            for match in matches:
                short.write(match + "\n")

        return matches


    def extract_commands(self):
        # TODO: Extract the commands.json logs.

        # "[00:00:13 INFO]: \u001b[93mThe_4ngry_5quid joined the game\u001b[0m\r\n"
        # "[00:00:30 INFO]: The_4ngry_5quid issued server command: /time add 6000\r\n"


        original_log = f"{self.log_location}{self.original_name}"
        commands_log = f"{self.log_location}{self.commands_name}"

        # Extract all lines into an array.
        with open(original_log) as short:
            lines = [line.rstrip() for line in short]

        # If the joined logs are already added to shortened.log

        if Path(commands_log).is_file():
            if not self.logs_are_newer(lines):
                return []

        matches = []
        raw = []
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
                raw.append(line)

        # TODO: Only add if newer than the current logs!
        with open(commands_log, "a+") as commands:
            for match in matches:
                commands.write(match + "\n")

        shortened_log = f"{self.log_location}{self.shortened_name}"
        with open(shortened_log, "a+") as short:
            for match in matches:
                short.write(match + "\n")

        return matches

        return
