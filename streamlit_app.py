import streamlit as st
import requests
import pandas as pd
from datetime import date

API_URL = "http://localhost:8000"

st.title("TaskTracker Dashboard")

with st.sidebar:
    st.header("Add new habit")
    habit_name = st.text_input("Habit name")
    frequency = st.selectbox("Frequency", ["daily", "weekly"])
    if st.button("Add"):
        if habit_name:
            response = requests.post(f"{API_URL}/habits/", json={"name": habit_name, "frequency": frequency})
            if response.status_code == 200:
                st.success(f"Habit '{habit_name}' added!")
            else:
                st.error("Failed to add habit")

st.header("Your habits")
response = requests.get(f"{API_URL}/habits/")
if response.status_code == 200:
    habits = response.json()
    if habits:
        data = []
        for h in habits:
            data.append({"ID": h["id"], "Name": h["name"], "Frequency": h["frequency"], "Active": h["active"]})
        df = pd.DataFrame(data)
        st.dataframe(df)

        st.subheader("Check in for today")
        habit_id = st.number_input("Habit ID", min_value=1, step=1)
        if st.button("Check in"):
            log_resp = requests.post(f"{API_URL}/habits/{habit_id}/log")
            if log_resp.status_code == 200:
                st.success("Checked in!")
            else:
                st.error("Failed")
    else:
        st.info("No habits yet. Add one from the sidebar.")
else:
    st.error("Cannot connect to API. Make sure FastAPI is running on port 8000.")