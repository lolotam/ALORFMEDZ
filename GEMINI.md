# GEMINI.md - Hospital Pharmacy Management System

## Project Overview

This project is a comprehensive, web-based Hospital Pharmacy Management System designed to streamline pharmacy operations. Built with Python and the Flask framework, it provides a complete solution for inventory management, patient and prescription tracking, supplier coordination, and in-depth reporting. The system is modular, with functionalities separated into Flask Blueprints, and it uses a file-based database for data storage.

The application features a role-based access control system (Admin vs. Department User), with distinct permissions for each role. Advanced features include an AI chatbot for intelligent queries, photo management for patient records, bulk data operations, and a themable user interface.

**Key Technologies:**

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
*   **Database:** File-based (JSON)
*   **Deployment:** Gunicorn (for production), Docker

## Building and Running

### Development

1.  **Prerequisites:**
    *   Python 3.7+
    *   pip

2.  **Setup:**
    ```bash
    # Clone the repository
    git clone <your-repository-url>
    cd ALORFMDZ

    # Create and activate a virtual environment
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Running the Application:**
    ```bash
    python app.py
    ```
    The application will be available at `http://localhost:5045`.

### Docker

```bash
# Build the Docker image
docker build -t hospital-pharmacy .

# Run the container
docker run -p 5045:5045 hospital-pharmacy
```

### Production

For production environments, it is recommended to use a more robust setup:

*   **WSGI Server:** Gunicorn
*   **Web Server:** Nginx (as a reverse proxy)
*   **Database:** PostgreSQL

## Development Conventions

*   **Modular Architecture:** The application is organized into Flask Blueprints, with each blueprint representing a major feature (e.g., `medicines`, `patients`, `auth`). This promotes separation of concerns and makes the codebase easier to maintain.
*   **Configuration:** Application configuration is managed in the `config.py` file, with different configurations for development, production, and testing. Environment variables are used to store sensitive information.
*   **Database:** The project uses a custom file-based database abstraction located in `utils/database.py`. This allows for easy data manipulation without writing raw file I/O code in the blueprints.
*   **Helper Functions:** Common utility functions are stored in the `utils/helpers.py` file. This includes functions for authentication and other recurring tasks.
*   **Static Assets:** All frontend assets (CSS, JavaScript, images) are located in the `static` directory.
*   **Templates:** HTML templates are stored in the `templates` directory, organized into subdirectories corresponding to the blueprints.
