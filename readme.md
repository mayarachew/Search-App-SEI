# Search App

## Requirements

<!-- Data App: .env_app
Database: .env_mysql -->

For Search App, create an environment according to spec-file.txt
For MySQL Database, create an environment according to db/spec-file.txt

Obs: requirements.txt file has the packages for streamlit deploy.

## Getting Started

Create a file `secrets.toml` with the following content (replacing the values):

```
[connections.mysql]
dialect = <your_dialect>
host = <your_host>
port = <your_port>
database = <your_database>
username = <your_username>
password = <your_password>
```

Create a poython environment following the instructions of file `spec-file.txt`.

To activate environment:
$ conda activate .env_app

To run Search App:
$ streamlit run main_page.py

The `requirements.txt` is required for Streamlit deploy.