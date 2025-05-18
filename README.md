# Marketing Automation Report Generator

A Flask-based web application for generating marketing automation reports.

## Features

- User authentication
- Report generation form with multiple input options
- Automated data collection from external sources
- Modular and extensible architecture

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

4. Run the application:
```bash
flask run
```

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── auth/
│   ├── routes/
│   ├── services/
│   ├── scrapers/
│   ├── templates/
│   └── static/
├── config.py
├── requirements.txt
└── run.py
```

## Development

The application uses Flask Blueprints for modular organization and Flask-Login for authentication. The scraping functionality is implemented using Selenium WebDriver. 