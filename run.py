from app import create_app   # Import the factory function from app/__init__.py

app = create_app()           # Create a Flask app instance

if __name__ == "__main__":
    app.run(debug=True)      # Run in debug mode (auto reload, detailed errors)
