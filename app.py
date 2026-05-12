from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from werkzeug.utils import secure_filename
import psycopg2
import os

app = Flask(__name__)

# -------------------------
# Local File Upload Configuration
# -------------------------
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, prefix=""):
    """Save uploaded file locally and return its URL path."""
    if not file or not file.filename:
        return ""
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed")
    filename = secure_filename(file.filename)
    if prefix:
        name, ext = os.path.splitext(filename)
        filename = f"{prefix}_{name}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return f"/uploads/{filename}"

# -------------------------
# Database connection (local)
# -------------------------
def get_db_connection():
    """Return a PostgreSQL connection for local development."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            host="127.0.0.1",
            database="drivers_db",
            user="postgres",
            password="1234",
            port="5432"
        )

# -------------------------
# Create all tables (with location columns)
# -------------------------
def create_drivers_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            district TEXT,
            town TEXT,
            phone TEXT,
            truck_name TEXT,
            location TEXT,
            image1 TEXT,
            image2 TEXT,
            image3 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
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

def create_orders_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            district TEXT,
            town TEXT,
            truck_name TEXT,
            material_service TEXT,
            location TEXT,
            phone TEXT,
            image1 TEXT,
            image2 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


# Create all tables when app starts
create_drivers_table()
create_deals_table()
create_orders_table()

# -------------------------
# Serve uploaded files
# -------------------------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# -------------------------
# Routes (unchanged except /driver POST)
# -------------------------

@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    drivers = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template("sofery.html", drivers=drivers)

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

@app.route("/alldrivercards")
def alldrivercards():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    drivers = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template("alldrivercards.html", drivers=drivers)

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
# Driver Registration (UPDATED to handle location)
# -------------------------
@app.route("/driverdetails")
def driverdetails():
    return render_template("driverdetails.html")

@app.route("/driver", methods=["GET", "POST"])
def driver():
    if request.method == "POST":
        name = request.form["name"]
        district = request.form["district"]
        town = request.form["town"]
        phone = request.form["phone"]
        truck_name = request.form["truck_name"]
        location = request.form["location"]
    

       

        image1 = request.files.get("image1")
        image2 = request.files.get("image2")
        image3 = request.files.get("image3")

        url1 = save_image(image1, f"driver_{name}_1")
        url2 = save_image(image2, f"driver_{name}_2")
        url3 = save_image(image3, f"driver_{name}_3")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO drivers (name, district, town, phone, truck_name,
                                 location,image1, image2, image3)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
        """, (name, district, town, phone, truck_name,
              location,url1, url2, url3))
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
# Deals Section (unchanged)
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

    image1 = request.files.get("imageone")
    image2 = request.files.get("image2")

    url1 = save_image(image1, f"deal_{suppliername}_1")
    url2 = save_image(image2, f"deal_{suppliername}_2")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO deals (suppliername, materialname, tippername, location, phone, imageone, imagetwo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (suppliername, materialname, tippername, location, phone, url1, url2))
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
# Orders Table (unchanged)
# -------------------------
@app.route("/order")
def order_form():
    return render_template("order_form.html")

@app.route("/submit_order", methods=["POST"])
def submit_order():
    name = request.form["name"]
    district = request.form["district"]
    town = request.form["town"]
    truck_name = request.form["truck_name"]
    material_service = request.form["material_service"]
    location = request.form["location"]
    phone = request.form["phone"]

    image1 = request.files.get("image1")
    image2 = request.files.get("image2")

    url1 = save_image(image1, f"order_{name}_1")
    url2 = save_image(image2, f"order_{name}_2")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (name, district, town, truck_name, material_service, location, phone, image1, image2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, district, town, truck_name, material_service, location, phone, url1, url2))
    conn.commit()
    cursor.close()
    conn.close()

    return "Your order has been placed successfully! We will contact you soon."

@app.route("/view_orders")
def view_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    orders = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return render_template("view_orders.html", orders=orders)

@app.route("/edit_order/<int:order_id>")
def edit_order_form(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return "Order not found", 404
    columns = [desc[0] for desc in cursor.description]
    order = dict(zip(columns, row))
    cursor.close()
    conn.close()
    return render_template("edit_order.html", order=order)

@app.route("/update_order/<int:order_id>", methods=["POST"])
def update_order(order_id):
    name = request.form["name"]
    district = request.form["district"]
    town = request.form["town"]
    truck_name = request.form["truck_name"]
    material_service = request.form["material_service"]
    location = request.form["location"]
    phone = request.form["phone"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT image1, image2 FROM orders WHERE id = %s", (order_id,))
    old = cursor.fetchone()
    if not old:
        cursor.close()
        conn.close()
        return "Order not found", 404
    old_image1, old_image2 = old

    image1 = request.files.get("image1")
    image2 = request.files.get("image2")

    url1 = old_image1
    if image1 and image1.filename:
        url1 = save_image(image1, f"order_{name}_1")

    url2 = old_image2
    if image2 and image2.filename:
        url2 = save_image(image2, f"order_{name}_2")

    cursor.execute("""
        UPDATE orders
        SET name=%s, district=%s, town=%s, truck_name=%s, material_service=%s, location=%s, phone=%s, image1=%s, image2=%s
        WHERE id=%s
    """, (name, district, town, truck_name, material_service, location, phone, url1, url2, order_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('view_orders'))

@app.route("/delete_order/<int:order_id>")
def delete_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('view_orders'))

# -------------------------
# WhatsApp Webhook (unchanged)
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
# Search drivers by district & town (unchanged)
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

# ROUTE  THAT CREATES A LINK TO A PARTICULAR DRIVER CARD DETAILS

@app.route('/driver_details/<int:driver_id>')
def driver_details(driver_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers WHERE id = %s", (driver_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.close()
        conn.close()
        return "Driver not found", 404
    
    columns = [desc[0] for desc in cursor.description]
    driver = dict(zip(columns, row))
    
    cursor.close()
    conn.close()
    
    return render_template("driver_details.html", driver=driver)

# -------------------------
# Run the app
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
