from flask import Flask, render_template, redirect, url_for, flash, session, request
from contact_form import ContactForm

from dotenv import load_dotenv
load_dotenv()

import os
from supabase import Client, create_client
import httpx


app = Flask(__name__)
app.secret_key = 'cpda_secret_key'

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"    

@app.route("/")
def home():
    return render_template("index.html")    

@app.route("/home-bkk")
def homeBkk():
    return render_template("index_bkk.html")

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/join")
def join():
    return render_template("join.html")

@app.route("/about-us")
def aboutUs():
    return render_template("about-us.html")

@app.route("/get-involved")
def get_involved():
    return render_template("get-involved.html")

@app.route("/news-updates")
def news_updates():
    return render_template("news-updates.html")

@app.route("/vision")
def vision():
    return render_template("vision.html")

@app.route("/priorities")
def priorities():
    return render_template("priorities.html")

@app.route("/industries")
def industries():
    return render_template("industries.html")

@app.route("/agri-process")
def agri_process():
    return render_template("agri-process.html")

@app.route("/agriculture")
def agriculture():
    return render_template("agriculture.html")

@app.route("/mining")
def mining():
    return render_template("mining.html")

@app.route("/tourism")
def tourism():
    return render_template("tourism.html")

@app.route("/transportation")
def transportation():
    return render_template("transportation.html")

@app.route("/health-education")
def health_education():
    return render_template("health-education.html")

@app.route("/region")
def region():
    years = ["2024", "2023", "2022", "2021"]
    populations = [86781, 86298, 86005, 86547]

    age_groups = [
        "85 years and over", "80 to 84 years", "75 to 79 years", "70 to 74 years",
        "65 to 69 years", "60 to 64 years", "55 to 59 years", "50 to 54 years",
        "45 to 49 years", "40 to 44 years", "35 to 39 years", "30 to 34 years",
        "25 to 29 years", "20 to 24 years", "15 to 19 years", "10 to 14 years",
        "5 to 9 years", "0 to 4 years"
    ]

    men = [-200, -300, -400, -500, -600, -700, -800, -900, -950, -1000, -950, -900, -850, -800, -750, -700, -650, -600]
    women = [250, 350, 450, 550, 650, 750, 850, 950, 1000, 1050, 1000, 950, 900, 850, 800, 750, 700, 650]

    income_labels = [
        "$200,000 and over", "$150,000 to 199,999", "$125,000 to 149,999", "$100,000 to 124,999",
        "$90,000 to 99,999", "$80,000 to 89,999", "$70,000 to 79,999", "$60,000 to 69,999",
        "$50,000 to 59,999", "$45,000 to 49,999", "$40,000 to 44,999", "$35,000 to 39,999",
        "$30,000 to 34,999", "$25,000 to 29,999", "$20,000 to 24,999", "$15,000 to 19,999",
        "$10,000 to 14,999", "$5,000 to 9,999", "Under $5,000"
    ]
    households_2024 = [716, 1535, 1321, 1554, 936, 915, 982, 1013, 1111, 678, 622, 675, 592, 633, 843, 337, 140, 62, 40]
    return render_template("region.html", years=years, populations=populations, age_groups=age_groups, men=men, women=women, income_labels=income_labels, households_2024=households_2024)

@app.route('/contact-us', methods=['GET', 'POST'])
def contact_us():
    contact_form = ContactForm()

    if contact_form.validate_on_submit():
        try:
            supabase.table("contact_messages").insert({
                "name": contact_form.name.data,
                "email": contact_form.email.data,
                "message": contact_form.message.data
            }).execute()

            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('contact_us'))

        except Exception as e:
            print("Supabase Error:", e)
            flash("Something went wrong. Please try again later.", "danger")

    return render_template('contact-us.html', form=contact_form)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Logged in as admin', 'success')
            return redirect(url_for('contact_messages'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/contact-messages')
def contact_messages():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    try:
        response = supabase.table("contact_messages").select("*").order("id", desc=True).execute()
        messages = response.data
    except httpx.HTTPStatusError as e:
        flash(f"Failed to load messages: {e.response.text}", "danger")
        messages = []

    return render_template('admin/contact_message.html', messages=messages)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
