from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import re
from topsis_sneha_102303033.core import topsis
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure upload and result folders
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Configure email (use your SMTP details)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "snehagupta.outlook@gmail.com"
app.config["MAIL_PASSWORD"] = "smrf vxij fpfa grgq"
app.config["MAIL_DEFAULT_SENDER"] = "snehagupta.outlook@gmail.com"

mail = Mail(app)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        # 1. Get file
        if "file" not in request.files:
            message = "Input file is required."
            return render_template("index.html", message=message)

        f = request.files["file"]
        if f.filename == "":
            message = "No file selected."
            return render_template("index.html", message=message)

        filename = secure_filename(f.filename)
        input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        f.save(input_path)

        # 2. Get weights, impacts, email
        weights = request.form.get("weights", "").strip()
        impacts = request.form.get("impacts", "").strip()
        email = request.form.get("email", "").strip()

        # 3. Validate email
        if not EMAIL_REGEX.fullmatch(email):
            message = "Invalid email format."
            return render_template("index.html", message=message)

        # 4. Validate weights/impacts count and format
        w_list = [w.strip() for w in weights.split(",") if w.strip() != ""]
        i_list = [i.strip() for i in impacts.split(",") if i.strip() != ""]

        if len(w_list) == 0 or len(i_list) == 0:
            message = "Weights and impacts cannot be empty."
            return render_template("index.html", message=message)

        if len(w_list) != len(i_list):
            message = "Number of weights must be equal to number of impacts."
            return render_template("index.html", message=message)

        if any(i not in ["+", "-"] for i in i_list):
            message = "Impacts must be either + or -."
            return render_template("index.html", message=message)

        # 5. Run TOPSIS (output as CSV)
        output_filename = "topsis_result.csv"
        output_path = os.path.join(RESULT_FOLDER, output_filename)

        try:
            topsis(input_path, weights, impacts, output_path)
        except Exception as e:
            message = f"Error while running TOPSIS: {e}"
            return render_template("index.html", message=message)

        # 6. Email the result file
        try:
            msg = Message(
                subject="TOPSIS Result File",
                recipients=[email],
                body="Please find attached the TOPSIS result file."
            )
            with open(output_path, "rb") as fp:
                msg.attach(output_filename, "text/csv", fp.read())
            mail.send(msg)
            message = "Result file has been emailed successfully."
        except Exception as e:
            message = f"Error sending email: {e}"

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
