from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# DESTINATION DATA (IMPROVED 🔥)
# =========================
DESTINATIONS = {
    "india": {
        "Goa": {
            "desc": "Goa is one of India's most popular beach destinations, known for its vibrant nightlife, golden beaches, water sports, and Portuguese heritage. It is perfect for both relaxation and fun-filled vacations with friends.",
            "img": "goa.jpg"
        },
        "Kerala": {
            "desc": "Kerala, also known as God's Own Country, offers serene backwaters, houseboats, lush greenery, and rich cultural traditions. It is ideal for peaceful and scenic vacations.",
            "img": "kerala.jpg"
        },
        "Manali": {
            "desc": "Manali is a beautiful hill station in Himachal Pradesh, famous for snow-covered mountains, adventure sports like skiing and paragliding, and breathtaking views.",
            "img": "manali.jpg"
        },
        "Jaipur": {
            "desc": "Jaipur, the Pink City of India, is known for its royal palaces, forts, vibrant culture, and historic architecture. A perfect destination for heritage lovers.",
            "img": "jaipur.jpg"
        },
        "Kashmir": {
            "desc": "Kashmir is often called paradise on earth, with stunning valleys, snow-capped mountains, Dal Lake houseboats, and mesmerizing natural beauty.",
            "img": "kashmir.jpg"
        },
        "Andaman": {
            "desc": "Andaman Islands offer crystal-clear waters, white sandy beaches, coral reefs, and water adventures like scuba diving and snorkeling.",
            "img": "andaman.jpg"
        },
    },
    "international": {
        "Dubai": {
            "desc": "Dubai is a global luxury destination featuring skyscrapers, desert safaris, shopping malls, and world-class attractions like Burj Khalifa.",
            "img": "dubai.jpg"
        },
        "Paris": {
            "desc": "Paris, the city of love, is famous for the Eiffel Tower, art museums, charming cafes, and romantic atmosphere.",
            "img": "paris.jpg"
        },
        "Maldives": {
            "desc": "Maldives is a tropical paradise known for overwater villas, crystal-clear oceans, and luxury island resorts—perfect for honeymoon and relaxation.",
            "img": "maldives.jpg"
        },
        "Singapore": {
            "desc": "Singapore is a modern city-state known for its skyline, cleanliness, technology, and attractions like Marina Bay Sands and Gardens by the Bay.",
            "img": "singapore.jpg"
        },
        "Bali": {
            "desc": "Bali is a cultural paradise with temples, beaches, waterfalls, and a relaxing tropical vibe.",
            "img": "bali.jpg"
        },
    }
}

# =========================
# MODELS (UPDATED 🔥)
# =========================

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    destination = db.Column(db.String(50))
    people = db.Column(db.Integer)
    payment = db.Column(db.String(50))
    date = db.Column(db.String(50))   # ✅ NEW

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))


# =========================
# INIT DB
# =========================
with app.app_context():
    db.create_all()

    if not Admin.query.filter_by(username="admin").first():
        hashed_pw = generate_password_hash("1234")
        admin = Admin(username="admin", password=hashed_pw)
        db.session.add(admin)
        db.session.commit()


# =========================
# HOME
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            booking = Booking(
                name=request.form["name"],
                email=request.form["email"],
                destination=request.form["destination"],
                people=int(request.form["people"]),
                payment=request.form.get("payment", "Demo"),
                date=request.form.get("date")   # ✅ SAVE DATE
            )

            db.session.add(booking)
            db.session.commit()

            flash(f"✅ Booking Confirmed for {booking.name}!", "success")

        except Exception as e:
            print(e)
            flash("❌ Error occurred. Please try again.", "danger")

        return redirect("/")

    return render_template("index.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        admin = Admin.query.filter_by(
            username=request.form["username"]).first()

        if admin and check_password_hash(admin.password,
                                         request.form["password"]):
            session["admin"] = True
            flash("Login successful!", "success")
            return redirect("/admin")
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")


# =========================
# ADMIN
# =========================
@app.route("/admin")
def admin():
    if not session.get("admin"):
        flash("Please login first!", "warning")
        return redirect("/login")

    bookings = Booking.query.all()

    stats = {place: 0 for cat in DESTINATIONS.values() for place in cat}

    total_people = sum(b.people for b in bookings)
    revenue = total_people * 5000

    for b in bookings:
        if b.destination in stats:
            stats[b.destination] += 1

    return render_template(
        "admin.html",
        bookings=bookings,
        stats=stats,
        total=total_people,
        revenue=revenue
    )


# =========================
# EXPLORE
# =========================
@app.route("/explore")
def explore():
    return render_template(
        "explore.html",
        india=DESTINATIONS["india"],
        international=DESTINATIONS["international"]
    )


# =========================
# DESTINATION PAGE
# =========================
@app.route("/destination/<place>")
def destination(place):

    for category in DESTINATIONS.values():
        if place in category:
            return render_template(
                "destination.html",
                place=place,
                data=category[place]
            )

    flash("Destination not found!", "danger")
    return redirect("/")


# =========================
# WISHLIST
# =========================
@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out successfully!", "info")
    return redirect("/")


# =========================
# DELETE
# =========================
@app.route("/delete/<int:id>")
def delete_booking(id):
    if not session.get("admin"):
        return redirect("/login")

    booking = Booking.query.get(id)
    if booking:
        db.session.delete(booking)
        db.session.commit()
        flash("Booking deleted!", "info")

    return redirect("/admin")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)