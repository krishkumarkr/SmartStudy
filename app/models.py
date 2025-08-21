from . import db

def init_db():
    """
    Create tables if they do not exist.
    This mirrors schema.sql inside Python so we can bootstrap DB at app start.
    """
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source_type TEXT CHECK(source_type IN ('manual','pdf')) NOT NULL DEFAULT 'manual',
            filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id)
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            user_answer TEXT,
            is_correct BOOLEAN,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS weak_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            strength_score INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)


# ---------------- USER HELPERS ----------------
def create_user(name, email, password_hash):
    return db.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        name, email, password_hash
    )

def get_user_by_email(email):
    rows = db.execute("SELECT * FROM users WHERE email = ?", email)
    return rows[0] if rows else None


# ---------------- NOTES HELPERS ----------------
def add_note(user_id, title, content, source_type='manual', filename=None):
    return db.execute(
        "INSERT INTO notes (user_id, title, content, source_type, filename) VALUES (?, ?, ?, ?, ?)",
        user_id, title, content, source_type, filename
    )

def get_notes_by_user(user_id):
    return db.execute(
        "SELECT id, title, substr(content,1,200) AS preview, source_type, filename, created_at \
         FROM notes WHERE user_id = ? ORDER BY created_at DESC",
        user_id
    )

def get_note(user_id, note_id):
    rows = db.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", note_id, user_id)
    return rows[0] if rows else None


# ---------------- FLASHCARDS HELPERS ----------------
def add_flashcard(user_id, note_id, question, answer):
    return db.execute(
        "INSERT INTO flashcards (user_id, note_id, question, answer) VALUES (?, ?, ?, ?)",
        user_id, note_id, question, answer
    )

def get_flashcards_by_note(user_id, note_id):
    return db.execute(
        "SELECT id, question, answer FROM flashcards WHERE user_id = ? AND note_id = ? ORDER BY id DESC",
        user_id, note_id
    )

def delete_flashcards_for_note(user_id, note_id):
    db.execute("DELETE FROM flashcards WHERE user_id = ? AND note_id = ?", user_id, note_id)



# ---------------- QUIZZES HELPERS ----------------
def create_quiz(user_id, title):
    return db.execute(
        "INSERT INTO quizzes (user_id, title) VALUES (?, ?)", user_id, title
    )

def add_quiz_question(quiz_id, question, correct_answer):
    return db.execute(
        "INSERT INTO quiz_questions (quiz_id, question, correct_answer) VALUES (?, ?, ?)",
        quiz_id, question, correct_answer
    )


# ---------------- WEAK TOPICS HELPERS ----------------
def add_weak_topic(user_id, topic, strength_score=0):
    return db.execute(
        "INSERT INTO weak_topics (user_id, topic, strength_score) VALUES (?, ?, ?)",
        user_id, topic, strength_score
    )

def get_weak_topics(user_id):
    return db.execute("SELECT * FROM weak_topics WHERE user_id = ?", user_id)
