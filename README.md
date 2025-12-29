# Task Management Application

A simple full-stack task management application with user authentication, built with Flask (backend) and Vanilla JavaScript (frontend).

## Tech Stack

- **Backend:** Python, Flask, SQLAlchemy, Flask-JWT-Extended
- **Frontend:** Vanilla JavaScript, HTML, CSS
- **Database:** SQLite

## Project Structure

```
/backend          # Flask API
  /auth           # Authentication module (register, login, logout)
  /tasks          # Task management module (CRUD operations)
  /migrations     # Database migrations (Alembic)
  app.py          # Application factory
  models.py       # Database models
  config.py       # Configuration
/frontend         # Static web files
  index.html      # Login/Register page
  tasks.html      # Task management page
  app.js          # JavaScript application logic
  style.css       # Styles
README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- pip

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:

   ```bash
   # Linux/macOS
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Initialize the database (if not already done):

   ```bash
   flask db upgrade
   ```

6. Run the Flask server:

   ```bash
   flask run
   ```

   The API will be available at `http://127.0.0.1:5000`

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Serve the static files using Python's built-in server:

   ```bash
   python -m http.server 8080
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8080/index.html
   ```

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint    | Description          | Body                                           |
| ------ | ----------- | -------------------- | ---------------------------------------------- |
| POST   | `/register` | Register new user    | `{name, email, password1, password2}`          |
| POST   | `/login`    | Login user           | `{email, password}`                            |
| POST   | `/refresh`  | Refresh access token | Requires refresh token in Authorization header |
| POST   | `/logout`   | Logout user          | Requires refresh token in Authorization header |

#### Register Response

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "user": { "id": 1, "name": "John", "email": "john@example.com" }
}
```

### Tasks (`/api/tasks`)

All task endpoints require JWT authentication (access token in Authorization header).

| Method | Endpoint | Description       | Body                              |
| ------ | -------- | ----------------- | --------------------------------- |
| GET    | `/`      | List user's tasks | -                                 |
| POST   | `/`      | Create new task   | `{title, description?, status?}`  |
| GET    | `/<id>`  | Get task by ID    | -                                 |
| PUT    | `/<id>`  | Update task       | `{title?, description?, status?}` |
| DELETE | `/<id>`  | Delete task       | -                                 |

#### Task Status Values

- `pending` (default)
- `in_progress`
- `done`

#### Task Response

```json
{
  "task": {
    "id": 1,
    "title": "My Task",
    "description": "Task description",
    "status": "pending",
    "created_at": "2025-12-29T12:00:00+00:00"
  }
}
```

## Features

### Backend

- User registration and login with password hashing
- JWT-based authentication with access/refresh tokens
- Token blocklist for logout functionality
- Full CRUD operations for tasks
- Users can only access their own tasks
- Input validation with Marshmallow schemas

### Frontend

- Login and registration screens with form validation
- Task list view with status indicators
- Create, edit, and delete tasks
- Update task status via dropdown
- Display task creation date
- Loading states and error handling
- Automatic token refresh on expiry
- Responsive design for mobile devices

## Assumptions Made

1. **Single-user sessions:** When a user logs in, all previous tokens are revoked
2. **SQLite for simplicity:** Using SQLite as the database for easy setup; can be switched to PostgreSQL/MySQL via config
3. **No email verification:** Registration does not require email verification
4. **Token expiry:** Access tokens expire after 15 minutes, refresh tokens after 30 days (Flask-JWT-Extended defaults)
5. **Password requirements:** Passwords must match during registration; no complexity requirements enforced
6. **Task ownership:** Tasks are strictly tied to the user who created them; no sharing functionality

## Environment Variables (Optional)

Create a `.env` file in the backend directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
```

## Feature Implementation

- Adding Pagination
- Docker setup
- Basic tests
