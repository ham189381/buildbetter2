from flask import Flask, request, render_template, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse
from werkzeug.utils import secure_filename
import psycopg2
import os
from urllib.parse import urlparse

app = Flask(__name__)

# -------------------------
# Configuration
# -------------------------
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------------------------
# Database connection
# -------------------------
def get_db_connection():
    """Return a PostgreSQL connection.
       For production (Render), use DATABASE_URL with SSL.
       For local development, fallback to hardcoded credentials."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Ensure SSL mode is required (Render enforces this for external connections)
        # Some DATABASE_URLs already include ?sslmode=require, but we add if missing.
        if "sslmode" not in database_url:
            # Append the parameter. Handle existing query string.
            separator = "&" if "?" in database_url else "?"
            database_url += f"{separator}sslmode=require"
        return psycopg2.connect(database_url)
    else:
        # Local development credentials – adjust as needed
        return psycopg2.connect(
            host="127.0.0.1",
            database="drivers_db",
            user="postgres",
            password="1234",
            port="5432"
        )

# -------------------------
# Helper to create tables
# -------------------------
def create_drivers_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            district TEXT,
            division TEXT,
            town TEXT,
            phone TEXT,
            truck_name TEXT,
            image1 TEXT,
            image2 TEXT,
            image3 TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def create_deals_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id SERIAL PRIMARY KEY,
            suppliername TEXT,
            materialname TEXT,
            tippername TEXT,
            location TEXT,
            phone TEXT,
            imageone TEXT,
            imagetwo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Create tables when app starts
create_drivers_table()
create_deals_table()

# -------------------------
# Routes (unchanged)
# -------------------------
@app.route("/")
def home():
    return render_template("sofery.html")

@app.route('/prospect')
def prospect():
    return render_template('prospect.html')

@app.route('/process', methods=['POST'])
def process():
    choice = request.form.get('option')
    if choice in ['supplire', 'driver', 'both']:
        return render_template("driverdetails.html")
    else:
        return '<h1>Result</h1><p>No option was selected.</p>'

@app.route("/drivers")
def view_drivers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers")
    drivers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("driverstable.html", drivers=drivers)

@app.route("/showdrivers")
def driverpage():
    return render_template("driver.html")

def get_drivers_by_town(town):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM drivers WHERE LOWER(town) LIKE LOWER(%s)",
        ('%' + town + '%',)
    )
    drivers = cursor.fetchall()
    cursor.close()
    conn.close()
    return drivers

@app.route("/drivers/<town>")
def show_drivers_by_town(town):
    drivers = get_drivers_by_town(town)
    return render_template("spacifictowndrivers.html", drivers=drivers, town=town)

# Static pages (unchanged)
@app.route('/kampaladistrict')
def kampaladistrict():
    return render_template('kampaladivisions.html')

@app.route('/wakisodistricttowns')
def wakisodistricttowns():
    return render_template('wakisodistricttowns.html')

@app.route('/mukonodistricttowns')
def mukonodistricttowns():
    return render_template('mukonodistricttowns.html')

@app.route('/nakawadivision')
def nakawadivision():
    return render_template('nakawadivisionparishes.html')

@app.route('/kawempedivision')
def kawempedivision():
    return render_template('kawempedivisionparishes.html')

@app.route('/kampalacentralsupplires')
def kampalacentralsupplires():
    return render_template('kampalacentralsupplires.html')

@app.route('/makindyedivision')
def makindyedivision():
    return render_template('makindyedivisionparishes.html')

@app.route('/rubagadivision')
def rubagadivision():
    return render_template('rubagadivisionparishes.html')

@app.route("/supplirenearyou")
def supplirenearyou():
    return render_template("supplirenearyou.html")

@app.route("/drivers_tables_by_town")
def drivers_tables_by_town():
    return render_template("drivers_by_town_table.html")

@app.route("/kampala_ntinda")
def kampala_ntinda():
    return render_template("kampala_ntinda_supplires.html")

# -------------------------
# Driver Registration
# -------------------------
@app.route("/driverdetails")
def driverdetails():
    return render_template("driverdetails.html")

@app.route("/driver", methods=["GET", "POST"])
def driver():
    if request.method == "POST":
        name = request.form["name"]
        district = request.form["district"]
        division = request.form["division"]
        town = request.form["town"]
        phone = request.form["phone"]
        truck_name = request.form["truck_name"]

        image1 = request.files["image1"]
        image2 = request.files["image2"]
        image3 = request.files["image3"]

        filename1 = secure_filename(image1.filename) if image1 else ""
        filename2 = secure_filename(image2.filename) if image2 else ""
        filename3 = secure_filename(image3.filename) if image3 else ""

        if filename1:
            image1.save(os.path.join(app.config["UPLOAD_FOLDER"], filename1))
        if filename2:
            image2.save(os.path.join(app.config["UPLOAD_FOLDER"], filename2))
        if filename3:
            image3.save(os.path.join(app.config["UPLOAD_FOLDER"], filename3))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO drivers (name, district, division, town, phone, truck_name, image1, image2, image3)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, district, division, town, phone, truck_name, filename1, filename2, filename3))
        conn.commit()
        cursor.close()
        conn.close()

        return "Driver information saved successfully"
    else:
        return render_template("driverdetails.html")

@app.route("/registereddrivers")
def registereddrivers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template("registereddriversview.html", data=data)

@app.route("/alldrivers")
def alldrivers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template("alldriversview.html", data=data)

# -------------------------
# Deals Section
# -------------------------
@app.route("/deals")
def deals():
    return render_template("dealsform.html")

@app.route("/save", methods=["POST"])
def save():
    suppliername = request.form["suppliername"]
    materialname = request.form["materialname"]
    tippername = request.form["tippername"]
    location = request.form["location"]
    phone = request.form["phone"]

    image1 = request.files["imageone"]
    image2 = request.files["image2"]

    filename1 = secure_filename(image1.filename) if image1 else ""
    filename2 = secure_filename(image2.filename) if image2 else ""

    if filename1:
        image1.save(os.path.join(app.config["UPLOAD_FOLDER"], filename1))
    if filename2:
        image2.save(os.path.join(app.config["UPLOAD_FOLDER"], filename2))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO deals (suppliername, materialname, tippername, location, phone, imageone, imagetwo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (suppliername, materialname, tippername, location, phone, filename1, filename2))
    conn.commit()
    cursor.close()
    conn.close()

    return "Your deal has been uploaded successfully"

@app.route("/table")
def table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deals")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template("table.html", data=data)

@app.route("/dealstocustomer")
def dealstocustomer():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deals")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template("customerdealsview.html", data=data)

@app.route("/dealstoadmin")
def dealstoadmin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM deals")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template("admindealsview.html", data=data)

@app.route("/dealspage")
def dealspage():
    return render_template("dealspage.html")

# -------------------------
# WhatsApp Webhook
# -------------------------
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if 'hello' in incoming_msg:
        msg.body("Hi there! 👋 send us your shopping items?")
    elif 'how are you' in incoming_msg:
        msg.body("I'm doing great, thanks for asking! 😊")
    elif 'bye' in incoming_msg:
        msg.body("Goodbye! Have a wonderful day! 👋")
    else:
        msg.body("Thanks for your message! I'm a simple bot. Try saying 'hello', 'how are you', or 'bye'.")

    return str(resp)

# -------------------------
# Search drivers by district & town
# -------------------------
@app.route("/searchdriverbydt")
def searchdriverbydt():
    return render_template("search_driver_by.html")

@app.route('/search_driversby', methods=['GET', 'POST'])
def search_driversby():
    district = request.form['district'].strip()
    town = request.form['town'].strip()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM drivers
        WHERE LOWER(district) = LOWER(%s)
        AND LOWER(town) = LOWER(%s)
    """, (district, town))

    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    drivers = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return render_template("drivers_results.html", drivers=drivers)

# -------------------------
# Run the app
# -------------------------
if __name__ == "__main__":
    # Use environment variable PORT if present (Render sets it), otherwise default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Disable debug mode when running on Render (i.e., when DATABASE_URL is set)
    debug = os.environ.get("DATABASE_URL") is None
    app.run(host="0.0.0.0", port=port, debug=debug)
