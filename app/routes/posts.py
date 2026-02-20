from __future__ import annotations

from werkzeug.utils import secure_filename
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.services import db, storage

posts_bp = Blueprint("posts", __name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _allowed_file(filename: str) -> bool:
    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[-1].lower() in allowed


def _validate_post_form(form, files) -> list[str]:
    errors: list[str] = []
    required = ["type", "item_name", "description", "location", "contact"]
    for field in required:
        if not form.get(field, "").strip():
            errors.append(f"'{field}' is required.")
    if form.get("type") not in ("lost", "found"):
        errors.append("'type' must be 'lost' or 'found'.")

    file = files.get("image")
    if file and file.filename:
        if not _allowed_file(file.filename):
            errors.append("Image must be jpg, jpeg, png, or webp.")
        else:
            # Read to check size, then seek back
            data = file.read()
            if len(data) > current_app.config["MAX_IMAGE_BYTES"]:
                errors.append("Image must be 5 MB or smaller.")
            file.seek(0)

    return errors


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@posts_bp.get("/")
def feed():
    posts = db.get_all_posts()
    return render_template("feed.html", posts=posts)


@posts_bp.get("/new")
def new_post_form():
    return render_template("new_post.html")


@posts_bp.post("/posts")
def create_post():
    errors = _validate_post_form(request.form, request.files)
    if errors:
        for err in errors:
            flash(err, "error")
        return render_template("new_post.html", form=request.form), 422

    # Optional image upload
    image_url: str | None = None
    file = request.files.get("image")
    if file and file.filename:
        safe_name = secure_filename(file.filename)
        try:
            image_url = storage.upload_image(file, safe_name)
        except Exception as exc:
            current_app.logger.exception("R2 upload failed: %s", exc)
            flash("Image upload failed. Post saved without image.", "warning")

    post_id = db.create_post(
        type=request.form["type"].strip(),
        item_name=request.form["item_name"].strip(),
        description=request.form["description"].strip(),
        location=request.form["location"].strip(),
        contact=request.form["contact"].strip(),
        image_url=image_url,
    )

    return redirect(url_for("posts.post_detail", post_id=post_id))


@posts_bp.get("/posts/<post_id>")
def post_detail(post_id: str):
    post = db.get_post_by_id(post_id)
    if post is None:
        abort(404)
    return render_template("post_detail.html", post=post)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@posts_bp.app_errorhandler(404)
def not_found(_e):
    return render_template("404.html"), 404


@posts_bp.app_errorhandler(413)
def too_large(_e):
    flash("File too large. Maximum image size is 5 MB.", "error")
    return render_template("new_post.html"), 413


@posts_bp.app_errorhandler(500)
def server_error(_e):
    return render_template("500.html"), 500
