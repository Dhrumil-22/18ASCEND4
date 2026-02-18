# ASCEND Project

## Project Structure
- **ascend-ui/**: Frontend user interface (HTML/CSS/JS).
- **backend/**: Flask backend application and database.

## How to Run

### 1. Backend Setup
The backend handles the database and API logic.

1.  Open a terminal and navigate to the `backend` directory:
    ```bash
    cd backend
    ```

2.  (Optional) Create and activate a virtual environment:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Initialize the database (if not already done):
    ```bash
    python init_db.py
    ```

5.  Run the server:
    ```bash
    python app.py
    ```
    The server will start at `http://127.0.0.1:5000`.

### 2. Frontend Setup
The frontend currently consists of static pages.

1.  Navigate to the `ascend-ui` folder.
2.  Open `index.html` in your web browser to view the Landing Page.
3.  Click "Sign In" to see the Login Page.

*Note: Currently, the frontend is static and does not yet communicate with the backend API.*
