"""Extract details from the minecraft logs and return them."""
from pathlib import Path
import json
from datetime import datetime


class MinecraftLogConverter:  # pylint: disable=too-few-public-methods
    """Main class to convert the logs."""
    def __init__(self):
        """Initialise the Minecraft Log Converter."""

        self.log_location = "/sharedFolder/Henry/Logs/Minecraft/"
        self.original_log = f"{self.log_location}minecraft-server.log"
        self.joined_log = f"{self.log_location}joined.log"
        self.commands_log = f"{self.log_location}commands.log"
        self.shortened_log = f"{self.log_location}minecraft-server-shortened.log"

    def run(self) -> dict:
        """Main function run by the endpoint."""
        # pylint: disable=too-many-locals
        # Initialise the sets.
        joined_set = set()
        commands_set = set()
        shortened_set = set()

        # Add each line in joined.log to the set.
        if Path(self.joined_log).is_file():
            with open(self.joined_log, "r", encoding="utf-8") as joined:
                for line in joined:
                    # Strip the newline character and add the line to the set.
                    joined_set.add(line.strip())

        # Add each line in commands.log to the set.
        if Path(self.commands_log).is_file():
            with open(self.commands_log, "r", encoding="utf-8") as commands:
                for line in commands:
                    # Strip the newline character and add the line to the set.
                    commands_set.add(line.strip())

        # Add each line in shortened.log to the set.
        if Path(self.shortened_log).is_file():
            with open(self.shortened_log, "r", encoding="utf-8") as short:
                for line in short:
                    # Strip the newline character and add the line to the set.
                    shortened_set.add(line.strip())

        # Extract the new joined logs and union with existing joined set.
        joined_extracted = self.extract(["joined ", "left ", "Banned "], "[93m", "\x1b")
        new_joined_set = set()
        for line in joined_extracted:
            username = line.split(" ")[0]
            timestamp = line.split(" - ")[-1]
            keyword = (
                "joined "
                if "joined " in line
                else "left " if "left " in line else "Banned "
            )

            # Convert into the format "2024-05-16T11:32:08.835486479Z left Giddle".
            new_joined_set.add(f"{timestamp} {keyword}{username}")
        joined_set = joined_set.union(new_joined_set)

        # Extract the new commands logs and union with existing commands set.
        commands_extracted = self.extract(["issued server command"], "]: ", "\r")
        new_commands_set = set()
        for line in commands_extracted:
            username = line.split(" ")[0]
            timestamp = line.split(" - ")[-1]
            command = line.split(": ")[1].split(" - ")[0]

            new_commands_set.add(f"{timestamp} command {username} '{command}'")
        commands_set = commands_set.union(new_commands_set)

        # Add joined and commands logs to shortened set.
        shortened_set = shortened_set.union(joined_set)
        shortened_set = shortened_set.union(commands_set)

        # Write out to the log files.
        latest_joined_line = ""
        with open(self.joined_log, "w", encoding="utf-8") as joined:
            for log in sorted(joined_set):
                joined.write(log + "\n")

                if "joined" in log:
                    latest_joined_line = log

        with open(self.commands_log, "w", encoding="utf-8") as commands:
            for log in sorted(commands_set):
                commands.write(log + "\n")

        with open(self.shortened_log, "w", encoding="utf-8") as short:
            for log in sorted(shortened_set):
                short.write(log + "\n")

        get_players = self.get_players()

        get_latest_connection = self.clean_date_output(latest_joined_line)

        return {
            # "joined": joined_set,
            # "commands": commands_set,
            "shortened": shortened_set,
            "players": get_players["players"],
            "count": get_players["count"],
            "last_connection": get_latest_connection,
        }

    def extract(self, keywords: list, prefix: str, suffix: str) -> set:
        """Extract lines containing the given keywords and remove content before the prefix and after the suffix.

        Args:
            keywords (list): List of keywords to return lines containing.
            prefix (str): All text before (and including) prefix will be removed.
            suffix (str): Content after (and including) the suffix will be removed.

        Returns:
            set: Set containing all lines with the keywords, with prefix/suffix content removed.
        """

        # Extract all lines into an array.
        with open(self.original_log, encoding="utf-8") as original:
            lines = [line.rstrip() for line in original]

        # Contains all lines containing the keywords
        matches = set()

        for line in lines:
            # pylint: disable=superfluous-parens
            if [line for keyword in keywords if (keyword in line)]:
                json_object = json.loads(line)

                timestamp = json_object["time"].split(".")[0]

                # Removing the prefix and trailing characters.
                log_details = json_object["log"]
                try:
                    log_shortened = log_details.split(prefix)[1]
                    log_shortened = log_shortened.split(suffix)[0]
                except IndexError:
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

            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return datetime.strptime("1999-01-01T01:01:01", "%Y-%m-%dT%H:%M:%S")

    def get_players(self) -> dict:
        """Returns all players who have ever connected.

        Returns:
            dict: List of the players connected and a count.
        """
        with open(self.joined_log, encoding="utf-8") as joined:
            lines = [line.rstrip() for line in joined]

        players = set()
        for line in lines:
            player = line.split(" ")[-1]
            players.add(player)

        result = {"players": players, "count": len(players)}

        return result

    def clean_date_output(self, line: str) -> str:
        """Takes the log date and converts it into "2024-05-25 at 13:00".

        Args:
            line (str): Raw log line.

        Returns:
            str: Cleaned up date output.
        """
        if line != "":
            date = line.split("T")[0]
            hour = line.split("T")[1].split(" ")[0]

            return f"{date} at {hour}"

        return ""
