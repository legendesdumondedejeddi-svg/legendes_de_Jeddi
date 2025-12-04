from flask import Flask, render_template, url_for

app = Flask(__name__)

# Adresse PayPal cachée
PAYPAL_EMAIL = "patrick.letoffet@gmail.com"

@app.context_processor
def inject_paypal():
    return dict(paypal_email=PAYPAL_EMAIL)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/don")
def don():
    return render_template("don.html")

@app.route("/apropos")
def apropos():
    return render_template("apropos.html")

@app.route("/grimoire")
def grimoire():
    return render_template("grimoire.html")

if __name__ == "__main__":
    app.run(debug=True)
