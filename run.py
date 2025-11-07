from dotenv import load_dotenv
from app import create_app


def main() -> None:
    """Entrypoint to run the Flask application using built-in server for development."""
    # Load environment variables from .env if present
    load_dotenv()

    app = create_app()
    # Bind to host/port from env or defaults
    host = app.config.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(app.config.get("FLASK_RUN_PORT", 5000))
    debug = bool(app.config.get("FLASK_DEBUG", True))
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()

