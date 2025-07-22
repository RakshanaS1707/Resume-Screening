import streamlit as st
import psycopg2
import pandas as pd

# Function to establish database connection
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="EMS",
        user="postgres",
        password="password",
        port="5432"
    )

# Fetch data from users table
def fetch_users():
    conn = get_connection()
    query = """
        SELECT * FROM login_user
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Fetch data from user_roles table
def fetch_user_roles():
    conn = get_connection()
    query = """
        SELECT * FROM login_role
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Streamlit app UI
st.title("PostgreSQL Data Viewer (Users & User Roles)")

option = st.sidebar.selectbox(
    "Select Table to View",
    ("Users", "User Roles")
)

if option == "Users":
    st.subheader("Users Table")
    try:
        users_df = fetch_users()
        st.dataframe(users_df)
    except Exception as e:
        st.error(f"Error fetching users data: {e}")

elif option == "User Roles":
    st.subheader("User Roles Table")
    try:
        user_roles_df = fetch_user_roles()
        st.dataframe(user_roles_df)
    except Exception as e:
        st.error(f"Error fetching user roles data: {e}")

if st.button("Refresh Data"):
    st.experimental_rerun()
