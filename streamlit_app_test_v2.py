import streamlit as st
import pandas as pd
import re
import random

# Email validation function
def validate_email(email):
    pattern = r'^[\w\.-]+@(?:wtwco\.com|towerswatson\.com)$'
    return re.match(pattern, email) is not None

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Name', 'Email', 'Time Slot', 'Password'])

if 'submission_message' not in st.session_state:
    st.session_state.submission_message = ""

st.title("WTW Blood Drive Application")

name = st.text_input("Name")
email = st.text_input("Email Address")
valid_email = validate_email(email)

# Form for user input
with st.form("blood_drive_form"):
    # name = st.text_input("Name")
    # email = st.text_input("Email Address")
    all_slots = [f"{date} {time}" for date in ["01/04/2024", "02/04/2024", "03/04/2024", "04/04/2024", "05/04/2024"]
                 for time in ["09:00 am", "10:00 am", "11:00 am"]]
    selection_counts = st.session_state.df['Time Slot'].value_counts()
    available_slots = [slot for slot in all_slots if selection_counts.get(slot, 0) < 3]
    date_time_option = st.selectbox("Select date and time", available_slots, index=0)
    # valid_email = validate_email(email)
    # The following error display is conditional based on invalid email
    if email and not valid_email:
        st.error("Please enter a valid work email address.")
        submit_button = st.form_submit_button("Submit", disabled=not valid_email)
    else:
        submit_button = st.form_submit_button("Submit")

# Handling form submission
if submit_button and name and email and valid_email:
    # Create new data frame for the new entry
    new_data = pd.DataFrame({'Name': [name], 'Email': [email], 'Time Slot': [date_time_option], 'Password': [random.randint(1000, 9999)]})
    # Remove existing entry for user and add new one
    st.session_state.df = pd.concat([st.session_state.df[(st.session_state.df['Name'] != name) | (st.session_state.df['Email'] != email)], new_data], ignore_index=True)
    st.session_state.submission_message = f"Your application has been successfully submitted. Your password is {new_data['Password'].iloc[0]}."
    # Re-run the app to display the success message
    st.experimental_rerun()

# Display submission message if it exists
if st.session_state.submission_message:
    st.success(st.session_state.submission_message)
    st.session_state.submission_message = ""  # Clear the message after displaying

# Admin panel
if 'admin_key' not in st.session_state:
    st.session_state.admin_key = ""

admin_key = st.sidebar.text_input("Admin", type="password", value=st.session_state.admin_key)

if admin_key == "admin_hunar":
    st.session_state.admin_key = admin_key  # Save admin key in session state
    if st.sidebar.button("Access Admin"):
        csv = st.session_state.df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(label="Download Results", data=csv, file_name='wtw_blood_drive_results.csv', mime='text/csv')

# New section for checking application status
st.sidebar.header("Check Application Status")
check_name = st.sidebar.text_input("Enter your name", key="check_name")
check_email = st.sidebar.text_input("Enter your email", key="check_email")
check_password = st.sidebar.text_input("Enter your password", key="check_password", type="password")

if st.sidebar.button("Check Status"):
    result = st.session_state.df.loc[(st.session_state.df['Name'] == check_name) & (st.session_state.df['Email'] == check_email) & (st.session_state.df['Password'].astype(str) == check_password)]
    if not result.empty:
        time_slot = result.iloc[0]['Time Slot']
        st.sidebar.success(f"Your time slot is {time_slot}.")
    else:
        st.sidebar.error("No matching records found.")

# Display current selection status
st.write("Current selection:")
for slot in all_slots:
    count = selection_counts.get(slot, 0)
    if count < 3:
        st.write(f"{slot}: {count}/3 available")
    else:
        st.write(f"{slot}: Fully booked")
