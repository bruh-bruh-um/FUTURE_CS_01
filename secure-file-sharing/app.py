import os
from io import BytesIO
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from crypto import encrypt_file, decrypt_bytes, hex_to_bytes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ENCRYPTION_KEY_HEX = os.getenv("ENCRYPTION_KEY_HEX")
ENCRYPTION_KEY = hex_to_bytes(ENCRYPTION_KEY_HEX)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret123")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv("MAX_CONTENT_LENGTH", 52428800))  # 50MB

@app.route("/", methods=["GET"])
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        flash("No file part", "danger")
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == "":
        flash("No selected file", "danger")
        return redirect(url_for('index'))
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".enc")
    file.save(filepath)  # save temporarily
    encrypt_file(filepath, ENCRYPTION_KEY)
    flash(f"File '{filename}' uploaded and encrypted!", "success")
    return redirect(url_for('index'))

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    enc_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Read encrypted file
    with open(enc_path, "rb") as f:
        encrypted_data = f.read()
    # Decrypt in memory
    decrypted_data = decrypt_bytes(encrypted_data, ENCRYPTION_KEY)
    # Send decrypted file to browser without saving to disk
    return send_file(
        BytesIO(decrypted_data),
        as_attachment=True,
        download_name=filename.replace(".enc", ""),
    )

if __name__ == "__main__":
    app.run(debug=True)
