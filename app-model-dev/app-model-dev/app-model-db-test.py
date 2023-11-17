# Import libraries
import streamlit as st
import psycopg2
import os

# Database Credentials
DBNAME=os.getenv("DBNAME") 
USER=os.getenv("USER")
HOST= os.getenv("HOST")
DBPORT=os.getenv("DBPORT")
DBPASSWORD=os.getenv("DBPASSWORD")
# Cloud Credential
PROJECT_NAME=os.getenv("PROJECT_NAME")

try: 
    # Connect to a database
    con = psycopg2.connect(f"""
                           dbname={DBNAME}
                           user={USER}
                           host={HOST}
                           port={DBPORT}
                           password={DBPASSWORD}
                           """)
    cur = con.cursor()
    st.write("Connected")
except:
    st.write("Not connected")

# Query
# SQL = st.text_area("Query here")
# if SQL:
#    st.write(cur.execute(SQL))
#    st.write(con.commit()) 

# Close Connection
cur.close()
con.close()
st.write("The connection has been disconnected.")