from flask import Flask, request,render_template,redirect,url_for
from twilio.twiml.messaging_response import MessagingResponse
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)

#---DATABASE SET UP ---this sets up the database ,it should 
#be written exactly here and just on top of all the routes

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE = os.path.join(PROJECT_FOLDER, "Database.db")

#this enables to upload images in a database 
# ie images are stored as file name in static/uploads 

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create directory if it doesn't exist
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_drivers_database():
    return sqlite3.connect(DATABASE_FILE)

#------ROUTES---------------

@app.route("/index")
def index():
    return  render_template("sofery.html")


@app.route('/prospect')
def prospect():
    return render_template('prospect.html') #prospect option form

@app.route('/process', methods=['POST'])
def process():
    # Get the selected radio button value
    choice = request.form.get('option')
    
    # Process the data
    if choice == 'supplire':
        message = "You selected am a supplire!"
        
    elif choice == 'driver':
       return render_template("driverdetails.html")
    
    elif choice == 'both':
        message = "You selected i do both!"
    else:
        message = "No option was selected."
    
    return f'<h1>Result</h1><p>{message}</p>'



#function to connect to database

def get_db_connection():
    return sqlite3.connect("database.db")



# handle form submision


#route to show all registered drivers(drivers table)

@app.route("/drivers")
def view_drivers():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM drivers")
    drivers = cursor.fetchall()

    conn.close()

    return render_template("driverstable.html", drivers=drivers)









#registered drivers page
@app.route("/showdrivers")
def driverpage():
    return render_template("driver.html")

#get drivers by town case insensitive

def get_drivers_by_town(town):
    conn=get_drivers_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM drivers WHERE LOWER(town) LIKE LOWER(?)",
        ('%' + town + '%',)
    )

    drivers = cursor.fetchall()
    conn.close()

    return drivers

get_drivers_by_town("town")

#route that uses the above function to show 
# drivers depending on town. 

#NOTE:We are going to link to this function in the html 
# page that contains towns and just chane 
# the town names in order to display drivers
# drivers database table in 
# that particular town

@app.route("/drivers/<town>")
def show_drivers_by_town(town):
    drivers = get_drivers_by_town(town)
    return render_template("spacifictowndrivers.html", drivers=drivers,town=town)




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


#routes to links in the naviation bar

@app.route("/supplirenearyou")
def supplirenearyou():
    return render_template("supplirenearyou.html")

#route that shows the page for drivers 
# table by town 

@app.route("/drivers_tables_by_town")
def drivers_tables_by_town():
    return render_template("drivers_by_town_table.html")

#routes to the different drivers in particular towns

@app.route("/kampala_ntinda")
def kampala_ntinda():
    return render_template("kampala_ntinda_supplires.html")








#DRIVER UPLOAD APP SECTION

# -------------------------
# CREATE TABLE drivers IF NOT EXISTS
# -------------------------
def createdriverstable():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    district TEXT,
    division TEXT,
    town TEXT,
    phone NUMBER,
    truck_name TEXT,
    image1 TEXT,
    image2 TEXT,
    image3 TEXT                   
    )
    """)

    conn.commit()
    conn.close()

createdriverstable()



#-------------------------
#DRIVERS REGISTRATION FORM PAGE
#--------------------------

@app.route("/driverdetails")
def driverdetails():
    return render_template("driverdetails.html")

# -------------------------
# SAVE DRIVER DATA
# -------------------------


@app.route("/driver",methods=["GET" ,"POST"])
def driver():
  
    name=request.form["name"]
    district=request.form["district"]
    division=request.form["division"]
    town=request.form["town"]
    phone=request.form["phone"]
    truck_name=request.form["truck_name"]

    image1=request.files["image1"]
    image2=request.files["image2"]
    image3=request.files["image3"]

    filename1 = ""
    filename2 = ""
    filename3 = ""

    if image1:
        filename1 = secure_filename(image1.filename)
        image1.save(os.path.join(app.config["UPLOAD_FOLDER"], filename1))
    
    if image2:
        filename2 = secure_filename(image2.filename)
        image2.save(os.path.join(app.config["UPLOAD_FOLDER"], filename2))

    if image3:
        filename3 = secure_filename(image3.filename)
        image3.save(os.path.join(app.config["UPLOAD_FOLDER"], filename3))

    #insert into database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO drivers (name,district,division,town,phone,truck_name,image1,image2,image3)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (name,district,division,town,phone,truck_name,filename1,filename2,filename3))

    conn.commit()
    conn.close()

    return "driver informationsaved successfully"



# -------------------------
#ADMIN ROUTE THAT SHOWS ALL THE REGISTERED DRIVERS
#  TABBLE WITH IMAGES FILE NAMES
# -------------------------
@app.route("/registereddrivers")
def registereddrivers ():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM drivers")
    data = cursor.fetchall()

    conn.close()
    return render_template("registereddriversview.html", data=data)

# -------------------------


# -------------------------
#ADMIN ROUTE THAT SHOWS ALL DETAILS OF DRIVERS WITH IMAGES
# -------------------------
@app.route("/alldrivers")
def alldrivers():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM drivers")
    data = cursor.fetchall()

    conn.close()
    return render_template("alldriversview.html", data=data)

# -------------------------





#HOT DEALS APP SECTION

# -------------------------
# CREATE TABLE deals IF NOT EXISTS
# -------------------------
def create_table():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        suppliername TEXT,
        materialname TEXT,
        tippername TEXT,
        location TEXT,
        phone TEXT,
        imageone TEXT,
        imagetwo TEXT
    )
    """)

    conn.commit()
    conn.close()

create_table()

# -------------------------
# FORM PAGE
# -------------------------
@app.route("/deals")
def deals():
    return render_template("dealsform.html")

# -------------------------
# SAVE DATA
# -------------------------
@app.route("/save", methods=["POST"])
def save():
    suppliername = request.form["suppliername"]
    materialname = request.form["materialname"]
    tippername = request.form["tippername"]
    location = request.form["location"]
    phone = request.form["phone"]

    image1 = request.files["imageone"]
    image2 = request.files["image2"]

    filename1 = ""
    filename2 = ""

    if image1:
        filename1 = secure_filename(image1.filename)
        image1.save(os.path.join(app.config["UPLOAD_FOLDER"], filename1))

    if image2:
        filename2 = secure_filename(image2.filename)
        image2.save(os.path.join(app.config["UPLOAD_FOLDER"], filename2))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO deals 
    (suppliername, materialname, tippername, location, phone, imageone, imagetwo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (suppliername, materialname, tippername, location, phone, filename1, filename2))

    conn.commit()
    conn.close()

    return "your deal has been uploaded successfully"

# -------------------------
# SHOW TABLE WITH FILENAMES
# -------------------------
@app.route("/table")
def table():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM deals")
    data = cursor.fetchall()

    conn.close()
    return render_template("table.html", data=data)

# -------------------------
#CUSTOMER ROUTE THAT RETURNS REGISTERED DEALS
#EXCLUDING DRIVER NAME AND PHONE 
# -------------------------
@app.route("/dealstocustomer")
def dealstocustomer():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM deals")
    data = cursor.fetchall()

    conn.close()
    return render_template("customerdealsview.html", data=data)

# -------------------------


# -------------------------
#ADMIN ROUTE THAT SHOWS ALL THE DETAILS IN REGISTERED DEALS
# -------------------------
@app.route("/dealstoadmin")
def dealstoadmin():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM deals")
    data = cursor.fetchall()

    conn.close()
    return render_template("admindealsview.html", data=data)

# -------------------------

#route that provides a link to the deals second page
@app.route("/dealspage")
def dealspage():
    return render_template("dealspage.html")





@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    # Get the incoming message from the user
    incoming_msg = request.values.get('Body', '').lower()
    
    # Create a Twilio response object
    resp = MessagingResponse()
    msg = resp.message()
    
    # Simple response logic
    if 'hello' in incoming_msg:
        msg.body("Hi there! 👋 send us your shopping items?")
    elif 'how are you' in incoming_msg:
        msg.body("I'm doing great, thanks for asking! 😊")
    elif 'bye' in incoming_msg:
        msg.body("Goodbye! Have a wonderful day! 👋")
    else:
        msg.body("Thanks for your message! I'm a simple bot. Try saying 'hello', 'how are you', or 'bye'.")
    
    return str(resp)


#flask receive and save images



@app.route("/", methods=["GET"])
def form():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("image")

    if not file or file.filename == "":
        return "No file selected"

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    return redirect(url_for("gallery", filename=filename))


#flask route to show the uploaded images

@app.route("/gallery/<filename>")
def gallery(filename):
    return render_template("gallery.html", filename=filename)



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000, debug=True)