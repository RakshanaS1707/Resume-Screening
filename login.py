import streamlit as st
import sqlite3
import hashlib



def get_connection():
    conn = sqlite3.connect('EMS.db')
    return conn

def create_users_table():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    conn = get_connection()
    conn.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, hash_password(password)))
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = get_connection()
    cursor = conn.execute("SELECT password FROM Users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True
    return False



create_users_table()

st.title("Login / Signup System using Streamlit")

menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

if menu == "Signup":
    st.subheader("Create New Account")

    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')

    if st.button("Signup"):
        if new_user and new_password:
            try:
                add_user(new_user, new_password)
                st.success("Account created successfully! Go to Login Menu.")
            except sqlite3.IntegrityError:
                st.error("Username already exists. Please choose a different username.")
        else:
            st.error("Please enter username and password.")

elif menu == "Login":
    st.subheader("Login to Your Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        if verify_user(username, password):
            st.success(f"Welcome {username}! 🎉 You are logged in.")
            # st.write("Successfully Loggedin")
        else:
            st.error("Invalid username or password. Please try again.")
