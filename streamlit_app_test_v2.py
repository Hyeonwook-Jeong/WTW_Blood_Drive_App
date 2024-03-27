import streamlit as st
import pandas as pd
import re
import random
import sqlite3

conn = sqlite3.connect('wtw_blood_drive.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS applications (
    Name TEXT,
    Email TEXT,
    Time_Slot TEXT,
    Password TEXT
)
''')
conn.commit()

def validate_email(email):
    pattern = r'^[\w\.-]+@(?:wtwco\.com|towerswatson\.com)$'
    return re.match(pattern, email) is not None

st.title("WTW Blood Drive Appointment Booking")

name = st.text_input("Name")
email = st.text_input("Email Address")
valid_email = validate_email(email)

with st.form("blood_drive_form"):
    all_slots = [
    "Monday 15/04/2024 13:10", "Monday 15/04/2024 14:30", 
    "Tuesday 16/04/2024 12:00", "Tuesday 16/04/2024 13:00", "Tuesday 16/04/2024 14:00", 
    "Wednesday 17/04/2024 11:40", "Wednesday 17/04/2024 12:40", "Wednesday 17/04/2024 13:40", "Wednesday 17/04/2024 14:40",
    "Thursday 18/04/2024 11:00", "Thursday 18/04/2024 12:00", "Thursday 18/04/2024 13:00", "Thursday 18/04/2024 14:00"]
    c.execute('SELECT Time_Slot, COUNT(*) as count FROM applications GROUP BY Time_Slot')
    selection_counts = {row[0]: row[1] for row in c.fetchall()}
    available_slots = [slot for slot in all_slots if selection_counts.get(slot, 0) < 4]
    date_time_option = st.selectbox("Select date and time", available_slots, index=0)
    if email and not valid_email:
        st.error("Please enter a valid work email address.")
        submit_button = st.form_submit_button("Submit", disabled=True)
    else:
        submit_button = st.form_submit_button("Submit")

if submit_button and name and email and valid_email:
    password = str(random.randint(1000, 9999))

    c.execute('DELETE FROM applications WHERE Name = ? AND Email = ?', (name, email))
    c.execute('INSERT INTO applications (Name, Email, Time_Slot, Password) VALUES (?, ?, ?, ?)',
              (name, email, date_time_option, password))
    conn.commit()
    st.success(f"Your application has been successfully submitted. Your password is {password}.")

# Display current selection status
st.write("Current selection:")
# Refresh selection counts from the database before displaying
c.execute('SELECT Time_Slot, COUNT(*) as count FROM applications GROUP BY Time_Slot')
selection_counts = {row[0]: row[1] for row in c.fetchall()}

for slot in all_slots:
    count = selection_counts.get(slot, 0)
    if count < 4:
        st.write(f"{slot}: {count}/4")
    else:
        st.write(f"{slot}: Fully booked")

# Admin panel
admin_key = st.sidebar.text_input("Admin")
if admin_key == "admin_hunar":
    if st.sidebar.button("Access Admin"):
        c.execute('SELECT * FROM applications')
        df = pd.DataFrame(c.fetchall(), columns=['Name', 'Email', 'Time Slot', 'Password'])
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(label="Download Results", data=csv, file_name='wtw_blood_drive_results.csv', mime='text/csv')

# New section for checking application status
st.sidebar.header("Check Appointment Status")
check_name = st.sidebar.text_input("Enter your name", key="check_name").strip()
check_email = st.sidebar.text_input("Enter your email", key="check_email").strip()
check_password = st.sidebar.text_input("Enter your password", key="check_password").strip()

if st.sidebar.button("Check Status"):
    c.execute('SELECT * FROM applications WHERE Name = ? AND Email = ? AND Password = ?', (check_name, check_email, check_password))
    result = c.fetchone()
    if result:
        st.sidebar.success(f"Your time slot is {result[2]}.")
    else:
        st.sidebar.error("No matching records found.")

