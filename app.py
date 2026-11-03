from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import socket
import datetime

app = Flask(__name__)
app.secret_key = "apt_cyber_matrix_ultra_secret_key_kali"

# Multi-user storage with Role-Based Access Control (RBAC)
USERS = {
    "admin": {
        "password": "admin123",
        "role": "Admin",
        "created_at": "SYSTEM_CORE"
    },
    "operator1": {
        "password": "op123",
        "role": "SecOps Analyst",
        "created_at": "DEFAULT"
    }
}

@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if username in USERS and USERS[username]["password"] == password:
            session["logged_in"] = True
            session["user"] = username
            session["role"] = USERS[username]["role"]
            return redirect(url_for("dashboard"))
        else:
            error = "ACCESS_DENIED: Invalid CallSign or Passcode."
            
    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    hostname = socket.gethostname()
    try:
        host_ip = socket.gethostbyname(hostname)
    except:
        host_ip = "127.0.0.1"
        
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    return render_template(
        "dashboard.html",
        user=session.get("user"),
        role=session.get("role"),
        host_ip=host_ip,
        current_time=current_time,
        users=USERS
    )

@app.route("/api/add_user", methods=["POST"])
def add_user():
    if not session.get("logged_in") or session.get("role") != "Admin":
        return jsonify({"status": "error", "message": "FORBIDDEN: Admin privileges required."}), 403
    
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "SecOps Analyst").strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password cannot be empty."}), 400

    if username in USERS:
        return jsonify({"status": "error", "message": "User callsign already exists in registry."}), 400

    USERS[username] = {
        "password": password,
        "role": role,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    return jsonify({"status": "success", "message": f"User [{username}] created with role [{role}]."})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
