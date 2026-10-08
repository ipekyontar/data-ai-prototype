# Data & AI Prototype: Natural-Language Querying on MySQL with Streamlit

A Streamlit + MySQL prototype for exploring automotive customer, vehicle and service-satisfaction data by asking questions in plain language (Turkish). A rule-based natural-language-to-SQL engine turns each question into a parameterized SQL query, runs it on MySQL, and shows the results together with the executed SQL for transparency.

The project was designed to be quick to set up and easy to extend. It was built with an AI-assisted ("vibe coding") approach for rapid prototyping.

## Features

- **Natural-language query interface:** ask questions such as "Benzinli araclarda memnuniyeti 4 puan uzeri olanlar" (petrol vehicles with satisfaction above 4) in a chat-style UI.
- **Rule-based NL-to-SQL engine:** recognizes fuel type, city, brand, service type and satisfaction thresholds from keywords, then builds the SQL dynamically.
- **Parameterized queries:** all user-derived values are passed as query parameters (`%s`), not concatenated into the SQL string.
- **Live dashboard sidebar:** totals for customers, vehicles and service records, average satisfaction, and distributions by fuel type and city.
- **Transparency:** every answer includes an expandable section showing the exact SQL that was executed.
- **Friendly error handling:** database connection errors are caught and shown with clear messages in the UI.

## Project structure

```
data-ai-prototype/
├── app.py                # Streamlit application (UI)
├── config.py             # MySQL connection settings
├── requirements.txt
├── db/
│   ├── connection.py     # mysql-connector-python connection layer
│   ├── schema.sql        # Table definitions (musteriler, araclar, servis_kayitlari)
│   └── seed_data.py      # Creates the database and fills it with sample data
└── services/
    ├── nlu_engine.py     # Natural language -> SQL (rule-based)
    └── queries.py        # Ready-made queries for the sidebar statistics
```

## Data model

Three related tables:

- `musteriler` (customers): name, city, contact details, registration date
- `araclar` (vehicles): linked to a customer; brand, model, year, fuel type (electric, petrol, diesel, hybrid)
- `servis_kayitlari` (service records): linked to a vehicle; service date and type, cost, satisfaction score

The seed script generates synthetic sample data: 50 customers, 1-2 vehicles each, and 1-4 service records per vehicle. It can be re-run at any time; it resets and regenerates the data.

## Getting started (macOS)

**1. Install dependencies**

```bash
cd data-ai-prototype

# Optional but recommended: virtual environment
python3 -m venv venv
source venv/bin/activate

pip3 install -r requirements.txt
```

If MySQL is not installed yet (with Homebrew):

```bash
brew install mysql
brew services start mysql
```

If MySQL (for example via MySQL Workbench) is already running, skip this step.

**2. Configure the database connection**

Defaults in `config.py` target a local server: `localhost:3306`, user `root`, empty password. Connection settings can be overridden with the environment variables described at the top of `config.py` (for example, to set a password for the `root` user).

**3. Create the database and load sample data**

```bash
python3 db/seed_data.py
```

**4. Run the app**

```bash
streamlit run app.py
```

The app opens automatically in the browser at `http://localhost:8501`.

## Usage

- **Sidebar:** live statistics such as total customers, vehicles and service records, average satisfaction, and fuel type and city distributions.
- **Main area (chat):** ask questions in natural language (Turkish), for example:
  - "Elektrikli araclarla servise gelen memnuniyeti dusuk musteriler kimler?" (Which customers with electric vehicles have low satisfaction?)
  - "Istanbul'daki hibrit arac sahiplerinin memnuniyeti nedir?" (What is the satisfaction of hybrid vehicle owners in Istanbul?)
  - "Lastik degisimi yaptiran musteriler kimler?" (Which customers had a tyre service?)
  - "Benzinli araclarda memnuniyeti 4 puan uzeri olanlar" (Petrol vehicles with satisfaction above 4)
- Open **"Calistirilan SQL sorgusunu goster"** under any answer to see the generated SQL.

## How the NLU engine works

`services/nlu_engine.py` exposes `parse_soru(soru)`, which returns a dictionary with the SQL string, its parameters and a human-readable description of the applied filters.

1. The question is normalized (lower-cased, Turkish characters mapped to ASCII).
2. Keyword matching detects filters: fuel type, city, brand, satisfaction (low, high or a numeric threshold) and service type.
3. Matched filters become `WHERE` conditions with parameters, joined across customers, vehicles and service records.
4. If no filter matches, the engine falls back to a free-text search across customer name, city, brand and service type.
5. Results are ordered by service date (newest first) and limited to 200 rows.

**Why rule-based?** The engine runs without an external API key, which keeps the prototype simple and easy to run anywhere. The `parse_soru` function has a clear contract, so its body can later be replaced with an LLM call (a system prompt containing the database schema that asks the model to produce SQL) to upgrade it to a fully LLM-based NL-to-SQL layer, with the rest of the app unchanged.

## Troubleshooting

| Error | Possible fix |
|---|---|
| `MySQL baglantisi kurulamadi` (connection failed) | Make sure the MySQL server is running, for example with `mysqladmin -u root -p status` |
| `Unknown database` | `python3 db/seed_data.py` may not have been run yet |
| `Access denied for user 'root'` | Set the database password through the environment variable described in `config.py` |
| Port error | Confirm that MySQL is listening on port `3306` |

## Tech stack

Python, Streamlit, MySQL, `mysql-connector-python`.
