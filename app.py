from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector

app = Flask(__name__)

# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = "smart_blood_bank_secret_key"


# =========================================================
# MYSQL CONNECTION
# =========================================================

db = mysql.connector.connect(
    host="localhost",
    port=3500,
    user="root",
    password="YOUR_MYSQL_PASSWORD",
    database="bloodbank"
)

print("MySQL Connected Successfully!")


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin_logged_in"] = True

            return redirect("/admin")

        return render_template(
            "login.html",
            error="Invalid username or password!"
        )

    return render_template("login.html")


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop("admin_logged_in", None)

    return redirect("/")


# =========================================================
# DONOR REGISTRATION
# =========================================================

@app.route("/donor", methods=["GET", "POST"])
def donor():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        blood_group = request.form["blood_group"]
        city = request.form["city"]

        cursor = db.cursor()

        query = """
        INSERT INTO donors
        (name, email, phone, blood_group, city)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            name,
            email,
            phone,
            blood_group,
            city
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return """
        <h2>✅ Donor Registered Successfully!</h2>

        <p>
            Thank you for registering as a blood donor.
        </p>

        <br>

        <a href="/">
            ← Back to Home
        </a>

        <br><br>

        <a href="/donor">
            Register Another Donor
        </a>
        """

    return render_template("donor.html")


# =========================================================
# HOSPITAL REGISTRATION
# =========================================================

@app.route("/hospital", methods=["GET", "POST"])
def hospital():

    if request.method == "POST":

        hospital_name = request.form["hospital_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        city = request.form["city"]
        address = request.form["address"]
        password = request.form["password"]

        cursor = db.cursor()

        query = """
        INSERT INTO hospitals
        (hospital_name, email, phone, city, address, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            hospital_name,
            email,
            phone,
            city,
            address,
            password
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return """
        <h2>✅ Hospital Registered Successfully!</h2>

        <p>
            Your hospital has been registered
            in the Smart Blood Bank system.
        </p>

        <br>

        <a href="/">
            ← Back to Home
        </a>

        <br><br>

        <a href="/hospital-login">
            🏥 Hospital Login
        </a>
        """

    return render_template("hospital.html")


# =========================================================
# HOSPITAL LOGIN
# =========================================================

@app.route("/hospital-login", methods=["GET", "POST"])
def hospital_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor()

        cursor.execute("""
            SELECT id, hospital_name, email
            FROM hospitals
            WHERE email = %s
            AND password = %s
        """, (email, password))

        hospital_data = cursor.fetchone()

        cursor.close()

        if hospital_data:

            session["hospital_id"] = hospital_data[0]
            session["hospital_name"] = hospital_data[1]
            session["hospital_email"] = hospital_data[2]

            return redirect("/hospital-dashboard")

        return render_template(
            "hospital_login.html",
            error="Invalid email or password!"
        )

    return render_template("hospital_login.html")


# =========================================================
# HOSPITAL DASHBOARD
# =========================================================

@app.route("/hospital-dashboard")
def hospital_dashboard():

    if "hospital_id" not in session:
        return redirect("/hospital-login")

    hospital_id = session["hospital_id"]

    cursor = db.cursor()

    # Hospital details
    cursor.execute("""
        SELECT hospital_name,
               email,
               phone,
               city,
               address
        FROM hospitals
        WHERE id = %s
    """, (hospital_id,))

    hospital_data = cursor.fetchone()

    if not hospital_data:

        cursor.close()

        session.pop("hospital_id", None)
        session.pop("hospital_name", None)
        session.pop("hospital_email", None)

        return redirect("/hospital-login")

    # Hospital requests
    cursor.execute("""
        SELECT id,
               hospital_name,
               phone,
               blood_group,
               units,
               request_date,
               status
        FROM blood_requests
        WHERE hospital_name = %s
        ORDER BY id DESC
    """, (hospital_data[0],))

    requests_list = cursor.fetchall()

    cursor.close()

    return render_template(
        "hospital_dashboard.html",

        hospital_name=hospital_data[0],
        hospital_email=hospital_data[1],
        hospital_phone=hospital_data[2],
        hospital_city=hospital_data[3],
        hospital_address=hospital_data[4],

        requests_list=requests_list
    )


# =========================================================
# HOSPITAL LOGOUT
# =========================================================

@app.route("/hospital-logout")
def hospital_logout():

    session.pop("hospital_id", None)
    session.pop("hospital_name", None)
    session.pop("hospital_email", None)

    return redirect("/hospital-login")


# =========================================================
# BLOOD REQUEST
# =========================================================

@app.route("/request-blood", methods=["GET", "POST"])
def request_blood():

    if request.method == "POST":

        # If hospital is logged in, get details from DB
        if "hospital_id" in session:

            hospital_id = session["hospital_id"]

            cursor = db.cursor()

            cursor.execute("""
                SELECT hospital_name, phone
                FROM hospitals
                WHERE id = %s
            """, (hospital_id,))

            hospital_data = cursor.fetchone()

            if hospital_data:

                hospital_name = hospital_data[0]
                phone = hospital_data[1]

            else:

                cursor.close()

                return redirect("/hospital-login")

        else:

            hospital_name = request.form["hospital_name"]
            phone = request.form["phone"]

            cursor = db.cursor()

        blood_group = request.form["blood_group"]

        try:

            units = int(request.form["units"])

        except ValueError:

            cursor.close()

            return """
            <h2>❌ Invalid Units</h2>

            <p>
                Please enter a valid number of units.
            </p>

            <br>

            <a href="/request-blood">
                ← Back to Blood Request
            </a>
            """

        if units <= 0:

            cursor.close()

            return """
            <h2>❌ Invalid Units</h2>

            <p>
                Units must be greater than 0.
            </p>

            <br>

            <a href="/request-blood">
                ← Back to Blood Request
            </a>
            """

        # Check blood group exists
        cursor.execute("""
            SELECT units
            FROM blood_stock
            WHERE blood_group = %s
        """, (blood_group,))

        stock_data = cursor.fetchone()

        if not stock_data:

            cursor.close()

            return """
            <h2>❌ Blood Group Not Found</h2>

            <p>
                Selected blood group is not available
                in the blood stock.
            </p>

            <br>

            <a href="/request-blood">
                ← Back to Blood Request
            </a>
            """

        # Stock is NOT reduced here.
        # Stock reduces only after Admin Approval.

        cursor.execute("""
            INSERT INTO blood_requests
            (hospital_name, phone, blood_group, units, status)
            VALUES (%s, %s, %s, %s, 'Pending')
        """, (
            hospital_name,
            phone,
            blood_group,
            units
        ))

        db.commit()

        cursor.close()

        return f"""
        <h2>✅ Blood Request Submitted Successfully!</h2>

        <p>
            Your request is waiting for admin approval.
        </p>

        <p>
            Blood Group:
            <strong>{blood_group}</strong>
        </p>

        <p>
            Units:
            <strong>{units}</strong>
        </p>

        <p>
            Status:
            <strong>Pending</strong>
        </p>

        <br>

        <a href="/hospital-dashboard">
            ← Back to Hospital Dashboard
        </a>
        """

    return render_template(
        "request.html",
        hospital_name=session.get("hospital_name", ""),
        phone=""
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    cursor = db.cursor()

    # Total donors
    cursor.execute("""
        SELECT COUNT(*)
        FROM donors
    """)

    total_donors = cursor.fetchone()[0]

    # Total requests
    cursor.execute("""
        SELECT COUNT(*)
        FROM blood_requests
    """)

    total_requests = cursor.fetchone()[0]

    # Blood stock
    cursor.execute("""
        SELECT blood_group,
               units
        FROM blood_stock
        ORDER BY id
    """)

    stock = cursor.fetchall()

    # Donors
    cursor.execute("""
        SELECT id,
               name,
               email,
               phone,
               blood_group,
               city
        FROM donors
        ORDER BY id DESC
    """)

    donors = cursor.fetchall()

    # Blood requests
    cursor.execute("""
        SELECT id,
               hospital_name,
               phone,
               blood_group,
               units,
               request_date,
               status
        FROM blood_requests
        ORDER BY id DESC
    """)

    requests_list = cursor.fetchall()

    # Hospitals
    cursor.execute("""
        SELECT hospital_name,
               email,
               phone,
               city,
               address
        FROM hospitals
        ORDER BY id DESC
    """)

    hospitals = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin.html",

        total_donors=total_donors,
        total_requests=total_requests,

        stock=stock,
        donors=donors,
        requests_list=requests_list,
        hospitals=hospitals
    )


# =========================================================
# APPROVE BLOOD REQUEST
# =========================================================

@app.route("/approve-request/<int:request_id>")
def approve_request(request_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    cursor = db.cursor()

    # Get request details
    cursor.execute("""
        SELECT blood_group,
               units,
               status
        FROM blood_requests
        WHERE id = %s
    """, (request_id,))

    request_data = cursor.fetchone()

    if not request_data:

        cursor.close()

        return """
        <h2>❌ Request Not Found</h2>

        <br>

        <a href="/admin">
            ← Back to Admin Dashboard
        </a>
        """

    blood_group = request_data[0]
    requested_units = request_data[1]
    current_status = request_data[2]

    # Only Pending request can be approved
    if current_status != "Pending":

        cursor.close()

        return """
        <h2>⚠️ Request Already Processed</h2>

        <p>
            This request is no longer pending.
        </p>

        <br>

        <a href="/admin">
            ← Back to Admin Dashboard
        </a>
        """

    # Check current stock
    cursor.execute("""
        SELECT units
        FROM blood_stock
        WHERE blood_group = %s
    """, (blood_group,))

    stock_data = cursor.fetchone()

    if not stock_data:

        cursor.close()

        return """
        <h2>❌ Blood Group Not Found</h2>

        <br>

        <a href="/admin">
            ← Back to Admin Dashboard
        </a>
        """

    available_units = stock_data[0]

    # Check sufficient stock
    if available_units < requested_units:

        cursor.close()

        return f"""
        <h2>❌ Insufficient Blood Stock</h2>

        <p>
            Blood Group:
            <strong>{blood_group}</strong>
        </p>

        <p>
            Requested Units:
            <strong>{requested_units}</strong>
        </p>

        <p>
            Available Units:
            <strong>{available_units}</strong>
        </p>

        <br>

        <a href="/admin">
            ← Back to Admin Dashboard
        </a>
        """

    # Reduce stock after approval
    new_stock = available_units - requested_units

    cursor.execute("""
        UPDATE blood_stock
        SET units = %s
        WHERE blood_group = %s
    """, (
        new_stock,
        blood_group
    ))

    # Change request status
    cursor.execute("""
        UPDATE blood_requests
        SET status = 'Approved'
        WHERE id = %s
    """, (request_id,))

    db.commit()

    cursor.close()

    return """
    <h2>✅ Blood Request Approved Successfully!</h2>

    <p>
        Blood stock has been updated successfully.
    </p>

    <p>
        Request status changed to Approved.
    </p>

    <br>

    <a href="/admin">
        ← Back to Admin Dashboard
    </a>
    """


# =========================================================
# REJECT BLOOD REQUEST
# =========================================================

@app.route("/reject-request/<int:request_id>")
def reject_request(request_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    cursor = db.cursor()

    cursor.execute("""
        SELECT status
        FROM blood_requests
        WHERE id = %s
    """, (request_id,))

    request_data = cursor.fetchone()

    if not request_data:

        cursor.close()

        return """
        <h2>❌ Request Not Found</h2>

        <br>

        <a href="/admin">
            ← Back to Admin Dashboard
        </a>
        """

    current_status = request_data[0]

    if current_status != "Pending":

        cursor.close()

        return """
        <h2>⚠️ Request Already Processed</h2>

        <br>

        <a href="/admin">
            ← Back to Admin Dashboard
        </a>
        """

    cursor.execute("""
        UPDATE blood_requests
        SET status = 'Rejected'
        WHERE id = %s
    """, (request_id,))

    db.commit()

    cursor.close()

    return """
    <h2>❌ Blood Request Rejected</h2>

    <p>
        Request status changed to Rejected.
    </p>

    <p>
        Blood stock was not changed.
    </p>

    <br>

    <a href="/admin">
        ← Back to Admin Dashboard
    </a>
    """


# =========================================================
# FIND MATCHING DONOR
# =========================================================

@app.route("/match-donor", methods=["GET", "POST"])
def match_donor():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    matched_donors = []
    selected_group = ""
    searched = False

    # GET
    if request.method == "GET":

        selected_group = request.args.get(
            "blood_group",
            ""
        ).strip()

        if selected_group:

            searched = True

            cursor = db.cursor()

            cursor.execute("""
                SELECT name,
                       email,
                       phone,
                       blood_group,
                       city
                FROM donors
                WHERE blood_group = %s
                ORDER BY id DESC
            """, (selected_group,))

            matched_donors = cursor.fetchall()

            cursor.close()

    # POST
    elif request.method == "POST":

        selected_group = request.form.get(
            "blood_group",
            ""
        ).strip()

        if selected_group:

            searched = True

            cursor = db.cursor()

            cursor.execute("""
                SELECT name,
                       email,
                       phone,
                       blood_group,
                       city
                FROM donors
                WHERE blood_group = %s
                ORDER BY id DESC
            """, (selected_group,))

            matched_donors = cursor.fetchall()

            cursor.close()

    return render_template(
        "matching.html",
        matched_donors=matched_donors,
        selected_group=selected_group,
        searched=searched
    )


# =========================================================
# BLOOD STOCK
# =========================================================

@app.route("/stock")
def stock():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    cursor = db.cursor()

    cursor.execute("""
        SELECT blood_group,
               units
        FROM blood_stock
        ORDER BY id
    """)

    stock_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "stock.html",
        stock=stock_data
    )


# =========================================================
# UPDATE BLOOD STOCK
# =========================================================

@app.route("/update-stock", methods=["POST"])
def update_stock():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    blood_group = request.form["blood_group"]

    try:

        units = int(request.form["units"])

    except ValueError:

        return """
        <h2>❌ Invalid Units</h2>

        <p>
            Please enter a valid number.
        </p>

        <br>

        <a href="/stock">
            ← Back to Stock
        </a>
        """

    if units < 0:

        return """
        <h2>❌ Invalid Stock</h2>

        <p>
            Stock cannot be negative.
        </p>

        <br>

        <a href="/stock">
            ← Back to Stock
        </a>
        """

    cursor = db.cursor()

    cursor.execute("""
        UPDATE blood_stock
        SET units = %s
        WHERE blood_group = %s
    """, (
        units,
        blood_group
    ))

    db.commit()

    cursor.close()

    return """
    <h2>✅ Blood Stock Updated Successfully!</h2>

    <br>

    <a href="/admin">
        ← Back to Admin Dashboard
    </a>
    """


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=False
    )
