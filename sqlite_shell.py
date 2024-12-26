import sqlite3
import random
import json
import openpyxl
import os

class GenericShell:
    def __init__(self):
        self.mode = None
        self.conn = None
        self.custom_commands = {}
        self.load_custom_commands()

    def load_custom_commands(self):
        """Load custom commands from an external file."""
        try:
            with open("commands.json", "r") as file:
                self.custom_commands = json.load(file)
            print(self.custom_commands)    
            print("Custom commands loaded.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No valid custom commands file found. Proceeding without custom commands.")

    def set_mode(self, mode):
        """Set the operating mode of the shell."""
        if mode == "sqlite":
            self.mode = "sqlite"
            print("Mode set to SQLite. Use 'set file <path>' to connect to a database.")
        elif mode == "game":
            self.mode = "game"
            print("Mode set to Game. Type 'play' to start the game.")
        else:
            print(f"Unknown mode: {mode}")

    def set_file(self, file_path):
        """Set the file (e.g., SQLite database) for the current mode."""
        if self.mode == "sqlite":
            try:
                self.conn = sqlite3.connect(file_path)
                print(f"Connected to SQLite database: {file_path}")
            except sqlite3.Error as e:
                print(f"Error connecting to SQLite database: {e}")
        else:
            print("Set a mode before specifying a file (e.g., 'set mode sqlite').")

    def execute_sqlite_query(self, query):
        """Execute a query in SQLite mode."""
        try:
            # Check for export flag
            if " export " in query:
                query, file_path = query.rsplit(" export ", 1)
                file_path = file_path.strip()
                cursor = self.conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                if not rows:
                    print("No data to export.")
                    return

                workbook = openpyxl.Workbook()
                sheet = workbook.active

                # Write the column headers
                columns = [description[0] for description in cursor.description]
                sheet.append(columns)

                # Write the data rows
                for row in rows:
                    sheet.append(row)

                workbook.save(file_path+"output.xlsx")
                print(f"Data exported to Excel file: {file_path}")
            else:
                cursor = self.conn.cursor()
                cursor.execute(query)
                if query.strip().lower().startswith(("select", "pragma")):
                    rows = cursor.fetchall()
                    for row in rows:
                        print(row)
                else:
                    self.conn.commit()
                    print(f"Query executed successfully. {cursor.rowcount} rows affected.")
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def handle_custom_sqlite_commands(self, command):
        """Handle extended SQLite commands for easier interaction."""
        if command.startswith("list"):
            self.handle_list(command)
        elif command.startswith("print"):
            self.handle_print_command(command)
        elif command.startswith("delete"):
            self.handle_delete_command(command)
        elif command.startswith("update"):
            self.handle_update_command(command)
        else:
            print(f"Unknown custom SQLite command: {command}")

    def handle_print_command(self, command):
        """Handle print command for SQLite."""
        _, _, subcmd = command.partition("print")
        subcmd = subcmd.strip()
        if "from" in subcmd:
            columns, table_part = subcmd.split("from", 1)
            columns = columns.strip()
            table_details = table_part.strip().split("where", 1)
            table_name = table_details[0].strip()
            where_clause = f"WHERE {table_details[1].strip()}" if len(table_details) > 1 else ""
            query = f"SELECT {columns} FROM {table_name} {where_clause};"
            self.execute_sqlite_query(query)
        else:
            print("Invalid syntax. Use 'print <columns> from <table> [where <condition>]' format.")

    def handle_delete_command(self, command):
        """Handle delete command for SQLite."""
        _, _, subcmd = command.partition("delete")
        subcmd = subcmd.strip()
        if "from" in subcmd:
            table_part = subcmd.split("from", 1)[1].strip()
            table_details = table_part.split("where", 1)
            table_name = table_details[0].strip()
            where_clause = f"WHERE {table_details[1].strip()}" if len(table_details) > 1 else ""
            query = f"DELETE FROM {table_name} {where_clause};"
            self.execute_sqlite_query(query)
        else:
            print("Invalid syntax. Use 'delete from <table> [where <condition>]' format.")

    def handle_update_command(self, command):
        """Handle update command for SQLite."""
        _, _, subcmd = command.partition("update")
        subcmd = subcmd.strip()
        if "set" in subcmd:
            table_part, set_part = subcmd.split("set", 1)
            table_name = table_part.strip()
            set_details = set_part.strip().split("where", 1)
            set_clause = set_details[0].strip()
            where_clause = f"WHERE {set_details[1].strip()}" if len(set_details) > 1 else ""
            query = f"UPDATE {table_name} SET {set_clause} {where_clause};"
            self.execute_sqlite_query(query)
        else:
            print("Invalid syntax. Use 'update <table> set <column=value> [where <condition>]' format.")

    def handle_list(self, command):
        """Handle list commands for easier interaction."""
        _, _, subcmd = command.partition("list")
        subcmd = subcmd.strip()
        if subcmd.startswith("tables"):
            self.execute_sqlite_query("SELECT name FROM sqlite_master WHERE type='table';")
        elif subcmd.startswith("databases"):
            self.execute_sqlite_query("PRAGMA database_list;")
        elif subcmd.startswith("columns"):
            _, _, table_name = command.partition("columns")
            table_name = table_name.strip()
            if table_name:
                self.execute_sqlite_query(f"PRAGMA table_info({table_name});")
            else:
                print("Please specify a table name.")
        else:
            print(f"Unknown list command: {command}")

    def export_to_excel(self, query, file_path):
        """Export the result of a query to an Excel file."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                print("No data to export.")
                return

            workbook = openpyxl.Workbook()
            sheet = workbook.active

            # Write the column headers
            columns = [description[0] for description in cursor.description]
            sheet.append(columns)

            # Write the data rows
            for row in rows:
                sheet.append(row)

            workbook.save(file_path)
            print(f"Data exported to Excel file: {file_path}")
        except sqlite3.Error as e:
            print(f"SQL Error: {e}")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")

    def play_game(self):
        """Simple number guessing game."""
        print("Welcome to the number guessing game!")
        number_to_guess = random.randint(1, 100)
        attempts = 0

        while True:
            try:
                guess = input("Guess a number between 1 and 100 (or type 'exit' to quit): ").strip()
                if guess.lower() == "exit":
                    print("Exiting the game.")
                    break

                guess = int(guess)
                attempts += 1

                if guess < number_to_guess:
                    print("Too low! Try again.")
                elif guess > number_to_guess:
                    print("Too high! Try again.")
                else:
                    print(f"Congratulations! You guessed the number in {attempts} attempts.")
                    break

            except ValueError:
                print("Please enter a valid number or 'exit' to quit.")

    def show_help(self, command=None):
        """Show help information for commands."""
        general_help = (
            "General Commands:\n"
            "  set mode <mode> - Set the shell mode (sqlite or game).\n"
            "  set file <file_path> - Set the file for SQLite mode.\n"
            "  exit - Exit the shell.\n"
        )
        sqlite_help = (
            "SQLite Commands:\n"
            "  sql <query> - Execute a raw SQL query.\n"
            "  list tables - List all tables in the database.\n"
            "  list databases - List all attached databases.\n"
            "  list columns <table_name> - List columns of a table.\n"
            "  print <columns> from <table> [where <condition>] - Select and display data.\n"
            "  delete from <table> [where <condition>] - Delete rows from a table.\n"
            "  update <table> set <column=value> [where <condition>] - Update rows in a table.\n"
        )
        if command == "sqlite":
            print(sqlite_help)
        else:
            print(general_help + sqlite_help)

    def run_shell(self):
        """Start the interactive shell."""
        print("Welcome to the Debugger's Shell.")
        print("Type 'help' for a list of commands or 'help sqlite' for SQLite-specific commands.")
        while True:
            try:
                prompt = f"{self.mode if self.mode else 'shell'}> "
                command = input(prompt).strip()
                if command == "":
                    continue

                if command.lower() in ("exit", "quit", "bye"):
                    break

                if command.lower() == "clear":
                    os.system('cls' if os.name == 'nt' else 'clear')

                elif command.startswith("set mode"):
                    _, _, mode = command.partition(" ")[2].partition(" ")
                    self.set_mode(mode.strip())

                elif command.startswith("set file"):
                    _, _, file_path = command.partition(" ")[2].partition(" ")
                    self.set_file(file_path.strip())

                elif command.lower() == "help":
                    self.show_help()

                elif command.lower() == "help sqlite":
                    self.show_help("sqlite")

                elif self.mode == "sqlite":
                    if self.conn:
                        if command.startswith("sql "):
                            self.execute_sqlite_query(command[4:])
                        elif command.startswith("list ") or command.startswith("print") or command.startswith("delete") or command.startswith("update"):
                            self.handle_custom_sqlite_commands(command)
                        elif command in self.custom_commands:
                            translated_command = self.custom_commands[command]
                            print(f"Executing custom command: {command}")
                            self.execute_sqlite_query(translated_command)
                        else:
                            self.execute_sqlite_query(command)
                    else:
                        print("No database connection. Use 'set file <path>' to connect to a database.")

                elif self.mode == "game":
                    if command.lower() == "play":
                        self.play_game()
                    else:
                        print("Unknown command in game mode. Use 'play' to start the game.")

                else:
                    print("Unknown command or mode not set.")

            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break
        self.close()

    def close(self):
        """Close any open connections."""
        if self.conn:
            self.conn.close()
        print("Bye!!!")

if __name__ == "__main__":
    shell = GenericShell()
    shell.run_shell()
