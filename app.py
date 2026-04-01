import io
from fpdf import FPDF 
from flask import Flask, send_file, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"
df = pd.read_excel("patients_extended.xlsx")

df.columns = df.columns.str.strip()

patients = []

df = pd.read_excel("patients_clean.xlsx")

patients = []

for _, row in df.iterrows():
    bp =str(row["bp"]).strip() 

# split safely
    try:
        parts = bp.replace(" ","").split('/')
        systolic = int(parts[0])
        diastolic = int(parts[1])
    except:
        systolic, diastolic = 0, 0

    patient = {
        "name": row["name"],
        "bp": bp,
        "systolic": systolic,
        "diastolic": diastolic,
        "pulse": row["pulse"],
        "glucose": row["glucose"],
        "heart_rate": row["heart_rate"],
        "doctor": row["doctor"],
        "care_manager": row["care_manager"],
        "mobile": row["mobile"],
        "password": str(row["password"]),

        "daily": [90, 95, 100, 92, 97],
        "weekly": [120, 125, 118, 121],
        "monthly": [70, 72, 75, 73]
    }

    patients.append(patient)

def generate_insights(patient):
    insights = []

    glucose = patient["glucose"]
    systolic = patient["systolic"]
    diastolic = patient["diastolic"]
    heart_rate = patient["heart_rate"]

    if glucose > 140:
        insights.append({
            "message": "Glucose is high",
            "risk": "High",
            "suggestion": "Reduce sugar intake"
        })

    if systolic > 130 or diastolic > 85:
        insights.append({
            "message": "Blood pressure is elevated",
            "risk": "High",
            "suggestion": "Reduce salt intake"
        })

    if heart_rate > 100:
        insights.append({
            "message": "Heart rate is high",
            "risk": "Moderate",
            "suggestion": "Avoid stress"
        })

    if not insights:
        insights.append({
            "message": "Vitals are normal",
            "risk": "Low",
            "suggestion": "Maintain lifestyle"
        })

    return insights


def find_patient(username, password):
    for p in patients:
        if p["name"].lower() == username.lower() and p["password"] == password:
            p["insights"] = generate_insights(p)
            return p
    return None


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        for p in patients:
            if p["name"] == username and p["password"] == password:
                session['user'] = username
                return redirect('/dashboard')

        return render_template("login.html", error="Invalid login")

    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    user = session['user']

    for p in patients:
        if p["name"] == user:
            p["insights"] = generate_insights(p)
            return render_template("dashboard.html", data=p)

@app.route('/reports')
def reports():
    username = session.get("user")

    if not username:
        return redirect(url_for('login'))

    patient = next((p for p in patients if p["name"] == username), None)

    if patient:
        patient["insights"] = generate_insights(patient)
        return render_template("report.html", data=patient)

    return redirect(url_for('login'))

@app.route('/doctor')
def doctor():
    username = session.get("user")

    if not username:
        return redirect(url_for('login'))

    patient = next((p for p in patients if p["name"] == username), None)

    if patient:
        return render_template("doctor.html", data=patient)

    return redirect(url_for('login'))

@app.route('/emergency')
def emergency():
    return "🚨 Care Manager and Hospital Notified!"

@app.route('/download-report')
def download_report():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "Patient Report", ln=True, align='C')
    pdf.ln(5)
    pdf.cell(0, 10, f"Name: {patient['name']}", ln=True)
    pdf.cell(0, 10, f"Systolic BP: {patient['systolic']}", ln=True)
    pdf.cell(0, 10, f"Diastolic BP: {patient['diastolic']}", ln=True)
    pdf.cell(0, 10, f"Pulse: {patient['pulse']}", ln=True)
    pdf.cell(0, 10, f"Glucose: {patient['glucose']}", ln=True)
    pdf.cell(0, 10, f"Heart Rate: {patient['heart_rate']}", ln=True)

    pdf_output = pdf.output(dest='S').encode('latin-1')
    pdf_buffer = io.BytesIO(pdf_output)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="report.pdf",
        mimetype="application/pdf"
    )

if __name__ == '__main__':
    app.run(debug=True)

print(df.columns)