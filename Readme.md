# SQLite Shell

SQLite Shell is an interactive command-line shell that allows you to interact with SQLite databases. The shell supports custom commands, SQL queries, and exporting query results to Excel files.

## Features

- **SQLite Mode**: Execute SQL queries, list tables, databases, and columns, and perform CRUD operations.
- **Custom Commands**: Load and execute custom commands from an external JSON file.
- **Export to Excel**: Export query results to Excel files.

## Requirements

- Python 3.x
- `openpyxl` library
- `pyinstaller` library

Install the required libraries using:
```sh
pip install -r requirements.txt
```

## Usage

1. Clone the repository:
    ```sh
    git clone https://github.com/arpitnema07/sqlite_shell
    cd sqlite_shell
    ```

2. Install the required libraries:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the shell:
    ```sh
    python shell.py
    ```

## Custom Commands

You can add custom commands by modifying the `commands.json` file. Each command should have a name and a corresponding SQL query or Python function to execute.

## Exporting to Excel

To export query results to an Excel file, use the `export` command followed by the query and the output file name.

## License

This project is licensed under the MIT License.
