# sql_agent

A natural language SQL agent that connects to a MySQL database (Chinook music dataset) and answers free-form questions by generating and executing SQL queries.

## How it works

Uses LangChain's `create_sql_agent` with the ReAct framework. The agent reasons step-by-step: inspects the database schema, writes a SQL query, executes it against MySQL, and returns the result in natural language. Accepts questions via CLI argument.

**Model:** IBM WatsonX Granite 3.2 8B Instruct

## Pattern

Agentic tool use, ReAct

## Tools

**LangChain**, **IBM WatsonX** (Granite), **MySQL**

## Setup

```bash
virtualenv my_env
source my_env/bin/activate

pip install ibm-watsonx-ai ibm-watson-machine-learning langchain langchain-community mysql-connector-python
```

### Database setup

Download and import the Chinook dataset into MySQL:

```bash
wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/Mauh_UvY4eK2SkcHj_b8Tw/chinook-mysql.sql
```

In the MySQL CLI:

```sql
SOURCE chinook-mysql.sql;
USE Chinook;
SELECT COUNT(*) FROM Album;
```

Update the connection string in `sql_agent.py`:

```python
mysql_username = 'root'
mysql_password = 'your_password'
mysql_host = 'your_host'
```

## Run

```bash
python sql_agent.py --prompt "Which country's customers spent the most by invoice?"
```

Example questions:
- `"How many employees are there"`
- `"How many albums are in the database?"`
- `"Can you left join Artist and Album by ArtistId? Show me 5 results."`
