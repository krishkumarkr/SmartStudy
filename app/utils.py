from functools import wraps
from flask import session, redirect, url_for, jsonify, request
import re


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            # If request is AJAX (expects JSON), return JSON
            if request.accept_mimetypes['application/json']:
                return jsonify({"reply": "⚠️ Please login first."}), 401
            # Otherwise redirect
            return redirect(url_for("routes.auth_page"))
        return f(*args, **kwargs)
    return decorated_function


