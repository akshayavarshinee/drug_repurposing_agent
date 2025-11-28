# Drug Repurposing Platform

A full-stack pharmaceutical research web application that allows researchers to query natural language questions about drug repurposing and receive AI-generated reports.

## Features

- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Natural Language Queries**: Submit pharmaceutical research questions
- **Report Generation**: Automatic generation of detailed pharmaceutical research reports
- **Report History**: View and access all past reports
- **Modern UI**: Clean, professional interface with custom color scheme

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database for data persistence
- **SQLAlchemy**: ORM for database operations
- **JWT**: Secure token-based authentication
- **Bcrypt**: Password hashing for security

### Frontend
- **HTML5 + Jinja2**: Template-based rendering
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: No heavy frontend frameworks

## Project Structure

```
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   ├── auth/
│   │   ├── routes.py           # Authentication endpoints
│   │   ├── hashing.py          # Password hashing utilities
│   │   └── jwt_handler.py      # JWT token management
│   ├── users/
│   │   ├── models.py           # User database model
│   │   └── routes.py           # User management endpoints
│   ├── queries/
│   │   ├── models.py           # Query database model
│   │   └── routes.py           # Query submission endpoints
│   └── results/
│       ├── models.py           # Report database model
│       └── routes.py           # Report retrieval endpoints
├── static/
│   ├── css/
│   │   └── styles.css          # Custom styling
│   └── js/
│       ├── main.js             # Common JavaScript
│       ├── auth.js             # Authentication logic
│       ├── query.js            # Query submission
│       ├── results.js          # Results display
│       └── history.js          # History page
├── templates/
│   ├── base.html               # Base template
│   ├── landing.html            # Landing page
│   ├── signup.html             # Registration page
│   ├── login.html              # Login page
│   ├── query.html              # Query/chat interface
│   ├── results.html            # Report display
│   └── history.html            # Report history
└── requirements.txt            # Python dependencies
```

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL database

### Environment Variables
The following environment variables are required:
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret key for JWT token generation

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The database tables will be created automatically on first startup.

3. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000
```

4. Access the application at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /auth/register`: Register new user
- `POST /auth/login`: Login user
- `POST /auth/logout`: Logout user

### Users
- `GET /users/profile`: Get current user profile

### Queries
- `POST /api/query/submit`: Submit a pharmaceutical research query

### Results
- `GET /api/results/{id}`: Get specific report by ID
- `GET /api/results/`: Get all reports for current user

## Database Schema

### Users
- id (Primary Key)
- username (Unique)
- email (Unique)
- hashed_password
- created_at

### Queries
- id (Primary Key)
- user_id (Foreign Key)
- question
- created_at

### Reports
- id (Primary Key)
- query_id (Foreign Key, Unique)
- user_id (Foreign Key)
- title
- report_text
- created_at

## Future Enhancements

- Integration with real pharmaceutical data APIs
- AI agent system for intelligent data retrieval
- PDF export functionality
- Data visualizations and charts
- Report sharing between users
- Advanced search and filtering

## Security

- Passwords are hashed using bcrypt
- JWT tokens for session management
- HTTPOnly cookies to prevent XSS attacks
- SQL injection prevention through SQLAlchemy ORM

## License

This project is for educational and research purposes.
