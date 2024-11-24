## Prerequisites
- Python > 3.10
- MySQL

## Installation
- Clone this repository 
- Activate virtual environment and install packages. `pip install -r requirements.txt`
- Create a new database and run [/database.sql](/database.sql) script to create tables and import data.
- Edit the database configuration in [/.env](/.env) file.

## Run project

- Run project `uvicorn src.main:app --reload`
- Navigate to http://localhost:8000