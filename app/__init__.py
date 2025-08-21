from flask import Flask
from cs50 import SQL
import os
from werkzeug.exceptions import RequestEntityTooLarge


# Database object (will be initialized in create_app)
db = None

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ---------------- CONFIG ----------------
    # Secret key is required for sessions, cookies, forms etc.
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "devkey")

    # Path to SQLite database inside instance/ folder
    db_path = os.path.join(app.instance_path, "smartstudy.db")


    # --- Folders ---
    os.makedirs(app.instance_path, exist_ok=True)
    # private uploads in instance/uploads
    upload_folder = os.path.join(app.instance_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = upload_folder
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB


    # Ensure the instance folder exists (to hold the DB)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return "File is too large! Max size is 16MB.", 413

     # ---------------- CREATE DB FILE IF MISSING ----------------
    if not os.path.exists(db_path):
        open(db_path, "w").close()   # create empty .db file

    # ---------------- INIT DB ----------------
    global db
    db = SQL(f"sqlite:///{db_path}")  # Initialize CS50 SQL with SQLite file

    # ---------------- INIT TABLES ----------------
    from . import models
    models.init_db()

    # ---------------- REGISTER ROUTES ----------------
    from . import routes
    app.register_blueprint(routes.bp)

    return app



