import os
from pathlib import Path
import shutil
import json
from datetime import datetime

class MinecraftLogConverter:  # pylint: disable=too-few-public-methods

    def __init__(self):
        """Initialise the Minecraft Log Converter."""

        self.log_location = "/sharedFolder/Henry/Logs/Minecraft/"
        self.original_name = "minecraft-server.log"
        self.joined_name = "joined.log"
        self.commands_name = "commands.log"
        self.shortened_name = "minecraft-server-shortened.log"

    def run(self) -> dict:
        """Main function run by the endpoint."""

        # TODO: CREATE A REFRESH METHOD
            # Puts the current joined.log and commands.log into a set.
            # Performs the run() method
            # Add the new joined.log and commands.log to the sets
                # A set, so that identical entries are removed
            # Write those sets into the joined.log and commands.log files

        log = f"{self.log_location}{self.original_name}"
        size = os.path.getsize(log)


        shortened_log = f"{self.log_location}{self.shortened_name}"
        # if Path(shortened_log).is_file():
        #     os.remove(shortened_log)

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

        return {f"{self.log_location}{self.shortened_name} updated": updated}


    def logs_are_newer(self, logs_to_add: list) -> bool:
        """Returns whether or not the logs_to_add are newer than the logs in shortened_name.

        Args:
            logs_to_add (list): List of the new logs to add to shortened.log

        Returns:
            bool: Whether the logs provided are newer or not.
        """

        # Immediately return false if the logs to add are empty.
        if logs_to_add == []:
            return False
        
        # Get the line of the oldest log.
        try:
            shortened_log = f"{self.log_location}{self.shortened_name}"
            with open(shortened_log) as short:
                lines = short.readlines()
                newest_in_shortened = lines[-1]
        # Entered if the shortened.log cannot be found.
        except FileNotFoundError as e:
            return True
        
        newest_in_logs_to_add = logs_to_add[-1]

        # If the logs to add are older than the existing logs in shortened_log (nothing to add)
        if self.get_date_from_string(newest_in_shortened) > self.get_date_from_string(newest_in_logs_to_add):
            return False
        
        # If the logs to add are newer than the existing logs in shortened_log, so must be added
        return True


    def get_date_from_string(self, line: str) -> datetime:
        """Returns the datetime from the given string.

        Args:
            line (str): Log line in the structure of "2024-05-16T11:32:08.835486479Z left Giddle".

        Returns:
            datetime: String converted to a datetime object.
        """
        # Shorten and convert the string.
        try:
            date_string = line.split(" ")[0]
            date_string = date_string.split(".")[0]

            return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S')
        # Return 1999 if it fails.
        except ValueError as e:
            return datetime.strptime("1999-01-01T01:01:01", '%Y-%m-%dT%H:%M:%S')


    def extract_joined(self) -> list:
        """Extract the joined, left and banned lines from the original log file.

        Returns:
            list: List containing all the new logs.
        """
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


    def extract_commands(self) -> list:
        """Extract the command lines from the original log file.

        Returns:
            list: List containing all the new logs.
        """
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
                except IndexError as e:
                    # Catches if this is not  command log.
                    continue

                
                matches.append(f"{timestamp} command {username} '{command}'")
                raw.append(line)

        with open(commands_log, "a+") as commands:
            for match in matches:
                commands.write(match + "\n")

        shortened_log = f"{self.log_location}{self.shortened_name}"
        with open(shortened_log, "a+") as short:
            for match in matches:
                short.write(match + "\n")

        return matches
