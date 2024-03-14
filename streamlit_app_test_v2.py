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

st.title("WTW Blood Drive Application")

name = st.text_input("Name")
email = st.text_input("Email Address")
valid_email = validate_email(email)

with st.form("blood_drive_form"):
    all_slots = [f"{date} {time}" for date in ["01/04/2024", "02/04/2024", "03/04/2024", "04/04/2024", "05/04/2024"]
                 for time in ["09:00 am", "10:00 am", "11:00 am"]]
    c.execute('SELECT Time_Slot, COUNT(*) as count FROM applications GROUP BY Time_Slot')
    selection_counts = {row[0]: row[1] for row in c.fetchall()}
    available_slots = [slot for slot in all_slots if selection_counts.get(slot, 0) < 3]
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
    if count < 3:
        st.write(f"{slot}: {count}/3 available")
    else:
        st.write(f"{slot}: Fully booked")

# Admin panel
admin_key = st.sidebar.text_input("Admin", type="password")
if admin_key == "admin_hunar":
    if st.sidebar.button("Access Admin"):
        c.execute('SELECT * FROM applications')
        df = pd.DataFrame(c.fetchall(), columns=['Name', 'Email', 'Time Slot', 'Password'])
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(label="Download Results", data=csv, file_name='wtw_blood_drive_results.csv', mime='text/csv')

# New section for checking application status
st.sidebar.header("Check Application Status")
check_name = st.sidebar.text_input("Enter your name", key="check_name").strip()
check_email = st.sidebar.text_input("Enter your email", key="check_email").strip()
check_password = st.sidebar.text_input("Enter your password", key="check_password", type="password").strip()

if st.sidebar.button("Check Status"):
    c.execute('SELECT * FROM applications WHERE Name = ? AND Email = ? AND Password = ?', (check_name, check_email, check_password))
    result = c.fetchone()
    if result:
        st.sidebar.success(f"Your time slot is {result[2]}.")
    else:
        st.sidebar.error("No matching records found.")

