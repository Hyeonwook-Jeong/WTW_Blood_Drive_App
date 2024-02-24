import streamlit as st
import pandas as pd
import re

# Email validation function
def validate_email(email):
    # Regular expression pattern for checking email format
    pattern = r'^[\w\.-]+@(?:wtwco\.com|towerswatson\.com)$' # Advanced settings
    if re.match(pattern, email):
        return True
    else:
        return False

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['Name', 'Email', 'Time Slot'])

st.title("WTW Blood Drive Application")

name = st.text_input("Name")
email = st.text_input("Email Address")

if name and email:
    # Disable Submit button if email is invalid or no available slots
    submit_disabled = not (validate_email(email))

    if submit_disabled:
        st.error("Please enter a valid work email address.")

all_slots = [f"{date} {time}" for date in ["01/04/2024", "02/04/2024", "03/04/2024", "04/04/2024", "05/04/2024"]
             for time in ["09:00 am", "10:00 am", "11:00 am"]]

selection_counts = st.session_state.df['Time Slot'].value_counts()

available_slots = [slot for slot in all_slots if selection_counts.get(slot, 0) < 3]
    
if name and email and available_slots:
    date_time_option = st.selectbox("Select date and time", available_slots)
    if st.button("Submit", disabled=submit_disabled):
        st.session_state.df = st.session_state.df[(st.session_state.df['Name'] != name) | (st.session_state.df['Email'] != email)]
        
        new_data = pd.DataFrame([[name, email, date_time_option]], columns=['Name', 'Email', 'Time Slot'])
        st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
        
        st.success("Your application successfully submitted.")
        st.experimental_rerun()

elif name and email:
    if validate_email(email):
        st.write("All slots are fully booked. Please check back later.")
    else:
        st.error("Please enter a valid email address.")

admin_key = st.sidebar.text_input("admin", key="admin_key")
if admin_key == "admin_hunar":
    if st.sidebar.button("Access"):
        st.sidebar.download_button(label="Download the result", data=st.session_state.df.to_csv(index=False).encode('utf-8'), file_name='wtw_blood_drive_application_result.csv', mime='text/csv')

st.write("Current selection:")
for slot in all_slots:
    count = selection_counts.get(slot, 0)
    if count < 3:
        st.write(f"{slot}: {count}/3")
    else:
        st.write(f"{slot}: Fully booked")
