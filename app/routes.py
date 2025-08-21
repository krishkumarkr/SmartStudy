import re
import os
import pdfplumber
from . import db
from PyPDF2 import PdfReader
from .utils import login_required
from werkzeug.utils import secure_filename
from .utils_ai import simple_flashcards_from_text
from pdfplumber.utils.exceptions import PdfminerException
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from .models import create_user, get_user_by_email, add_note, get_note, get_notes_by_user, add_flashcard, delete_flashcards_for_note, get_flashcards_by_note

bp = Blueprint("routes", __name__)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def is_valid_email(email):
    return re.match(EMAIL_REGEX, email)

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except Exception:
    HAS_PDFPLUMBER = False




# ---- allow only specific filetypes ----
ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
    return render_template("dashboard.html", user=user)

@bp.route("/")
def auth_page():
    session.pop("auth_step", None)  # reset conversation only
    return render_template("auth_chat.html")

@bp.route("/auth_chat", methods=["POST"])
def auth_chat():
    if "user_id" in session:
        return jsonify({"reply": "✅ You're logged in"})
    
    user_input = request.json.get("message", "").strip()

    # Always reset flow if user says "start" or session is stale
    if user_input.lower() in ["start", "restart", "reset"]:
        session.clear()
        session["auth_step"] = "ask_new_user"
        return jsonify({"reply": "🔄 Restarting... Hey! Are you a new user? (yes/no)"})

    # First time → start conversation
    if "auth_step" not in session:
        session["auth_step"] = "ask_new_user"
        return jsonify({"reply": "Hey! Are you a new user? (yes/no)"})

    step = session["auth_step"]

    # ---------------- NEW USER FLOW ----------------
    if step == "ask_new_user":
        if user_input.lower() in ["yes", "y"]:
            session["auth_step"] = "ask_name"
            return jsonify({"reply": "Great! What is your name?"})
        elif user_input.lower() in ["no", "n"]:
            session["auth_step"] = "login_email"
            return jsonify({"reply": "Welcome back! Please enter your email."})
        else:
            return jsonify({"reply": "❓ Please reply with 'yes' or 'no'."})


    elif step == "ask_name":
        session["temp_name"] = user_input
        session["auth_step"] = "signup_email"
        return jsonify({"reply": "What's your email?"})

    elif step == "signup_email":
        if not is_valid_email(user_input):
            return jsonify({"reply": "❌ Invalid email format. Please enter a valid email."})

        # Check if email already exists
        existing = db.execute("SELECT * FROM users WHERE email = ?", user_input)
        if existing:
            return jsonify({"reply": "⚠️ Email already exists. Please use another one."})

        session["temp_email"] = user_input
        session["auth_step"] = "signup_password"
        return jsonify({"reply": "Got it! Please set the password."})

    elif step == "signup_password":
        session["temp_password"] = user_input
        session["auth_step"] = "signup_confirm_password"
        return jsonify({"reply": "Please confirm the password, once again."})

    elif step == "signup_confirm_password":
        if user_input == session["temp_password"]:
            # Hash password before storing
            hashed_pw = generate_password_hash(session["temp_password"])

            # create_user(session["temp_name"], session["temp_email"], hashed_pw)
            db.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                       session["temp_name"], session["temp_email"], hashed_pw)

            # Clear temp fields
            session.pop("temp_name", None)
            session.pop("temp_email", None)
            session.pop("temp_password", None)

            session["auth_step"] = "post_signup"
            return jsonify({"reply": "You're successfully signed up 🎉 Do you want to login? (yes/no)"})
        else:
            session["auth_step"] = "signup_password"
            return jsonify({"reply": "Passwords didn't match ❌ Please set a password again."})

    elif step == "post_signup":
        if user_input.lower() in ["yes", "y"]:
            session["auth_step"] = "login_email"
            return jsonify({"reply": "Please enter your email."})
        elif user_input.lower() in ["no", "n"]:
            session.pop("auth_step", None)
            return jsonify({"reply": "Alright 👍 You can login later from here."})
        else:
            return jsonify({"reply": "❓ Please reply with 'yes' or 'no'."})

    # ---------------- LOGIN FLOW ----------------
    elif step == "login_email":
        if not is_valid_email(user_input):
            return jsonify({"reply": "❌ That doesn't look like a valid email. Please enter a correct email."})
    
        rows = db.execute("SELECT * FROM users WHERE email = ?", user_input)
        if not rows:
            return jsonify({"reply": "⚠️ This email is not registered. Please try again or signup."})

        session["temp_email"] = user_input
        session["auth_step"] = "login_password"
        return jsonify({"reply": "Please, enter the password"})

    elif step == "login_password":
        # rows = get_user_by_email(session["temp_email"])
        rows = db.execute("SELECT * FROM users WHERE email = ?", session["temp_email"])
        if rows and check_password_hash(rows[0]["password"], user_input):
            session["user_id"] = rows[0]["id"]
            session.pop("auth_step", None)
            return jsonify({"reply": "✅ You're logged in!"})
        else:
            session["auth_step"] = "login_email"
            return jsonify({"reply": "Incorrect Password ❌ Please enter your email again:"})

    return jsonify({"reply": "⚠️ Oops, something went wrong."})


# ---------------- LOGOUT ----------------
@bp.route("/logout")
def logout():
    session.clear()
    return jsonify({"reply": "👋 You've been logged out. Come back soon!"})


#  --------------------------------------------------------------------------------------------------------------
#  --------------------------------------------------------------------------------------------------------------

# -------- NOTES: list + form --------
@bp.route("/notes", methods=["GET"])
@login_required
def notes_page():
    # if not require_login_page():
    #     return redirect(url_for("routes.auth_page"))

    user_id = session["user_id"]
    notes = get_notes_by_user(user_id)
    return render_template("notes.html", notes=notes)

# -------- NOTES: save manual text --------
@bp.route("/notes/save_text", methods=["POST"])
@login_required
def notes_save_text():
    # if "user_id" not in session:
    #     return jsonify({"ok": False, "msg": "Please login."}), 401

    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        return jsonify({"ok": False, "msg": "Title and content are required."}), 400

    try:
        add_note(session["user_id"], title, content, source_type="manual", filename=None)
        return jsonify({"ok": True, "msg": "✅ Note saved!"})
    except Exception as e:
        # This will show the actual DB / Python error in your browser
        return jsonify({"ok": False, "msg": f"Error: {str(e)}"}), 500


# -------- NOTES: upload PDF --------
@bp.route("/notes/upload_pdf", methods=["POST"])
@login_required
def notes_upload_pdf():

    if "file" not in request.files:
        return jsonify({"ok": False, "msg": "No file uploaded."}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    title = request.form.get("title", "").strip() or (file.filename if file else "Untitled")

    if file.filename == "":
        return jsonify({"ok": False, "msg": "No selected file."}), 400

    if not allowed_file(file.filename):
        return jsonify({"ok": False, "msg": "Only pdf/txt/md allowed."}), 400

    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    content = ""
    ext = filename.rsplit(".", 1)[1].lower()

    try:
        if ext == "pdf":
            if HAS_PDFPLUMBER:
                try:
                    with pdfplumber.open(save_path) as pdf:
                        for page in pdf.pages:
                            content += (page.extract_text() or "") + "\n"
                except Exception as e:
                    # Catch password-protected or unreadable PDFs
                    return jsonify({"ok": False, "msg": "❌ PDF is encrypted or unreadable. Please upload an unlocked PDF."}), 400
            else:
                with open(save_path, "rb") as f:
                    reader = PdfReader(f)
                    if reader.is_encrypted:
                        return jsonify({"ok": False, "msg": "❌ PDF is encrypted. Please upload an unlocked version."}), 400
                    for page in reader.pages:
                        content += (page.extract_text() or "") + "\n"
        else:
            # txt / md
            with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

    except Exception as e:
        return jsonify({"ok": False, "msg": f"Error reading file: {str(e)}"}), 500

    content = content.strip()
    if not content:
        return jsonify({"ok": False, "msg": "Could not extract text from file."}), 400

    add_note(session["user_id"], title, content, source_type="pdf", filename=filename)
    return jsonify({"ok": True, "msg": "✅ PDF imported as note!", "filename": filename})


# -------- NOTES: view single --------
@bp.route("/notes/<int:note_id>", methods=["GET"])
@login_required
def notes_view(note_id):
    # if not require_login_page():
    #     return redirect(url_for("routes.auth_page"))
    note = get_note(session["user_id"], note_id)
    if not note:
        return "Not found", 404
    return render_template("note_detail.html", note=note)



# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------


# ---- Flashcards page ----
@bp.route("/flashcards")
@login_required
def flashcards_page():
    return render_template("flashcards.html")

# ---- List notes for dropdown ----
@bp.route("/api/notes", methods=["GET"])
@login_required
def api_notes():
    notes = get_notes_by_user(session["user_id"])
    # Return only what UI needs
    return jsonify([{"id": n["id"], "title": n["title"]} for n in notes])

# ---- Get existing flashcards for a note ----
@bp.route("/api/flashcards", methods=["GET"])
@login_required
def api_flashcards():
    note_id = request.args.get("note_id", type=int)
    if not note_id:
        return jsonify({"ok": False, "msg": "note_id required"}), 400
    cards = get_flashcards_by_note(session["user_id"], note_id)
    return jsonify({"ok": True, "cards": cards})

# ---- Generate flashcards from a note ----
@bp.route("/flashcards/generate", methods=["POST"])
@login_required
def generate_flashcards():
    data = request.get_json(silent=True) or {}
    note_id = data.get("note_id")
    count = int(data.get("count", 10))

    if not note_id:
        return jsonify({"ok": False, "msg": "note_id required"}), 400

    note = get_note(session["user_id"], note_id)
    if not note:
        return jsonify({"ok": False, "msg": "Note not found"}), 404

    if note["user_id"] != session["user_id"]:
        return jsonify({"ok": False, "msg": "Unauthorized"}), 403

    # (Optional) clear old cards for this note
    delete_flashcards_for_note(session["user_id"], note_id)

    # Generate
    pairs = simple_flashcards_from_text(note["content"], max_cards=count)
    if not pairs:
        return jsonify({"ok": False, "msg": "Could not generate flashcards from this note."}), 400

    for p in pairs:
        add_flashcard(session["user_id"], note_id, p["question"], p["answer"])

    return jsonify({"ok": True, "msg": f"Generated {len(pairs)} flashcards.", "cards": pairs})
