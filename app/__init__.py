from flask import Flask, flash, redirect, url_for
from .config import Config
from .routes.posts import posts_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Flask hard limit on incoming request body (covers multipart image upload)
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_IMAGE_BYTES

    app.register_blueprint(posts_bp)

    @app.errorhandler(413)
    def too_large(_e):
        """Request body exceeded MAX_CONTENT_LENGTH — flash error and return to form."""
        flash("Image is too large. Maximum file size is 5 MB.", "error")
        return redirect(url_for("posts.new_post_form"))

    return app
