from flask import Flask, render_template, request
import re, dns.resolver, smtplib

app = Flask(__name__)

def is_valid_email_format(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_mx_record(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return [str(mx.exchange) for mx in mx_records]
    except:
        return None

def verify_email_smtp(email):
    domain = email.split('@')[1]
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
    except:
        return False

    try:
        server = smtplib.SMTP(mx_record, 25, timeout=10)
        server.helo()
        server.mail('check@example.com')
        code, _ = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        email = request.form["email"]

        if not is_valid_email_format(email):
            result = "❌ Format email salah!"
        else:
            domain = email.split("@")[1]
            mx = check_mx_record(domain)
            if not mx:
                result = "❌ Domain tidak punya mail server (MX record)."
            else:
                if verify_email_smtp(email):
                    result = "✅ Email aktif & valid."
                else:
                    result = "⚠️ Domain valid, tapi email tidak bisa diverifikasi (bisa false)."

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
