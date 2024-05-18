import os
from pathlib import Path
import shutil
import json
from datetime import datetime

class MinecraftLogConverter:  # pylint: disable=too-few-public-methods

    def __init__(self):
        """Initialise the Minecraft Log Converter."""

        self.log_location = "/sharedFolder/Henry/Logs/Minecraft/"
        self.original_log = f"{self.log_location}minecraft-server.log"
        self.joined_log = f"{self.log_location}joined.log"
        self.commands_log = f"{self.log_location}commands.log"
        self.shortened_log = f"{self.log_location}minecraft-server-shortened.log"

    def run(self) -> dict:
        """Main function run by the endpoint."""

        # TODO:
            # Backup current logs
                # Create a HashSet of the logs in shortened.log
                # Create a set of logs in joined.log
                # Create a set of logs in commands.log
            # Add new logs
                # Use extract() to create a set of logs from original.log
                # For each log returned, add to either joined set or commands set
                # Add joined set and commands set to the shortened set
                # Write to joined.log, commands.log and shortened.log
        
        # Initialise the sets.
        joined_set = set()
        commands_set = set()
        shortened_set = set()

        # Add each line in joined.log to the set.
        if Path(self.joined_log).is_file():
            with open(self.joined_log, 'r') as joined:
                for line in joined:
                    # Strip the newline character and add the line to the set.
                    joined_set.add(line.strip())

        # Add each line in commands.log to the set.
        if Path(self.commands_log).is_file():
            with open(self.commands_log, 'r') as commands:
                for line in commands:
                    # Strip the newline character and add the line to the set.
                    commands_set.add(line.strip())

        # Add each line in shortened.log to the set.
        if Path(self.shortened_log).is_file():
            with open(self.shortened_log, 'r') as short:
                for line in short:
                    # Strip the newline character and add the line to the set.
                    shortened_set.add(line.strip())

        # Extract the new joined logs and union with existing joined set.
        joined_extracted = self.extract(["joined ", "left ", "Banned "], "[93m", "\x1b")
        new_joined_set = set()
        for line in joined_extracted:
            username = line.split(" ")[0]
            timestamp = line.split(" - ")[-1]
            keyword = "joined " if "joined " in line else "left " if "left " in line else "Banned "

            # Convert into the format 2024-05-16T11:32:08.835486479Z left Giddle
            new_joined_set.add(f"{timestamp} {keyword}{username}")
        joined_set = joined_set.union(new_joined_set)

        # Extract the new commands logs and union with existing commands set.
        commands_extracted = self.extract(["issued server command"], "]: ", "\r")
        new_commands_set = set()
        for line in commands_extracted:
            username = line.split(" ")[0]
            timestamp = line.split(" - ")[-1]

            print(line)
            command = line.split(": ")[1].split(" - ")[0]

            # Convert into the format 2024-05-16T11:32:08.835486479Z left Giddle
            new_commands_set.add(f"{timestamp} command {username} '{command}'")
            continue
        commands_set = commands_set.union(new_commands_set)

        # Add joined and commands logs to shortened set.
        shortened_set = shortened_set.union(joined_set)
        shortened_set = shortened_set.union(commands_set)

        # Write out to the log files.
        with open(self.joined_log, "w") as joined:
            for log in joined_set:
                joined.write(log + "\n")
        
        with open(self.commands_log, "w") as commands:
            for log in commands_set:
                commands.write(log + "\n")
        
        with open(self.shortened_log, "w") as short:
            for log in shortened_set:
                short.write(log + "\n")

        return {"Joined": joined_set, "Commands": commands_set, "Shortened": shortened_set}
        

    
    def extract(self, keywords: list, prefix: str, suffix: str) -> set:

        # Extract all lines into an array.
        with open(self.original_log) as original:
            lines = [line.rstrip() for line in original]

        # Contains all lines containing the keywords
        matches = set()
        
        for line in lines:
            if [line for keyword in keywords if(keyword in line)]:
                print(line)
                json_object = json.loads(line)

                timestamp = json_object["time"].split(".")[0]

                # Removing the prefix and trailing characters.
                log_details = json_object["log"]
                try:
                    log_shortened = log_details.split(prefix)[1]
                    log_shortened = log_shortened.split(suffix)[0]
                except IndexError as e:
                    # Catches if this is not joined/left/banned log.
                    continue

                matches.add(f"{log_shortened} - {timestamp}")

        return matches
    

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
        except ValueError as e:
            return datetime.strptime("1999-01-01T01:01:01", '%Y-%m-%dT%H:%M:%S')