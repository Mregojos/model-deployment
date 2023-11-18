#----------Import libraries----------# 
import streamlit as st
import psycopg2
import os
import time
# from env import *

#----------Database Credentials----------# 
DBNAME=os.getenv("DBNAME")
USER=os.getenv("USER")
HOST= os.getenv("HOST")
DBPORT=os.getenv("DBPORT")
DBPASSWORD=os.getenv("DBPASSWORD")
APP_PORT=os.getenv("APP_PORT")
APP_ADDRESS=os.getenv("APP_ADDRESS")
DOMAIN_NAME=os.getenv("DOMAIN_NAME")
# Cloud Credentials
PROJECT_NAME=os.getenv("PROJECT_NAME")

#----------Page Configuration----------# 
st.set_page_config(page_title="Matt Cloud Tech",
                   page_icon=":cloud:",
                   initial_sidebar_state="collapsed",
                   menu_items={
                       'About':"# Matt Cloud Tech"})

#----------About Me Section----------#
st.write("### :cloud: Matt Cloud Tech")
st.header("", divider="rainbow")

st.write("""
        ### Good day :wave:.
        ### My name is :blue[Matt]. I am a Cloud Technology Enthusiast. :technologist:
        ### Currently, I am learning and building Cloud Infrastructure, Data and CI/CD Pipelines, and Intelligent Systems. 
        """) 
# st.divider()
#----------End of About Me Section----------#
st.sidebar.empty()

#----------Portfolio Section----------#
with st.expander(' :notebook: Portfolio'):
    # Connect to a database
    con = psycopg2.connect(f"""
                           dbname={DBNAME}
                           user={USER}
                           host={HOST}
                           port={DBPORT}
                           password={DBPASSWORD}
                           """)
    cur = con.cursor()

    # Create a table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS portfolio(id serial PRIMARY KEY, project_name varchar, description varchar, link varchar)")
    con.commit()    
    st.write("### Project Collection")
    cur.execute("""
                SELECT * 
                FROM portfolio
                """)
    for id, project_name, description, link in cur.fetchall():
        st.write(f"### [{project_name}]({link})")
        st.write(f"{description}")
        st.divider()
    
    # Add new project
    add = st.checkbox("Modify")
    if add:
        password = st.text_input("Password", type="password")
        if password == DBPASSWORD:
            modify = st.text_input("Add or Delete")
            if modify == "Add":
                project_name = st.text_input("Project Name")
                description = st.text_input("Description")
                link = st.text_input("Link")
                ### Insert into adatabase
                save = st.button("Save")
                if save:
                    SQL = "INSERT INTO portfolio (project_name, description, link) VALUES(%s, %s, %s);"
                    data = (project_name, description, link)
                    cur.execute(SQL, data)
                    con.commit()
                    st.write("Successfully Added.")
                    st.button(":blue[Done]")
            elif modify == "Delete":
                project_name = st.text_input("Project Name")
                delete = st.button("Delete")
                if delete:
                    cur.execute(f"DELETE FROM portfolio WHERE project_name = '{project_name}';")
                    # SQL = "DELETE FROM portfolio WHERE project_name = %s;"
                    # data = (project_name)
                    # cur.execute(SQL, data)
                    con.commit()
                    st.success("Successfully Deleted.")
                    st.button(":blue[Done]")
            
#----------End of Portfolio Section----------#

#----------Notepad Section----------#
with st.expander(' :pencil: Notepad'):
    st.header(" :pencil: Notepad",divider="rainbow")
    st.caption("""
                Add your thoughts here. It will be stored in a database. \n
                :warning: :red[Do not add sensitive data.]
                """)
    # Connect to a database
    con = psycopg2.connect(f"""
                           dbname={DBNAME}
                           user={USER}
                           host={HOST}
                           port={DBPORT}
                           password={DBPASSWORD}
                           """)
    cur = con.cursor()

    # Create a table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS notes(id serial PRIMARY KEY, name varchar, header varchar, note varchar, time varchar)")
    con.commit()

    # Inputs
    name = st.text_input("Your Name")
    header = st.text_input("Header")
    note = st.text_area("Note")
    if st.button("Add a note"):
        time = time.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
        st.write(f""" \n
                ##### :pencil: {header} \n
                #### {note} \n
                :man: {name} \n""")
        st.caption(f":watch: {time}")
        st.success("Successfully Added.")
        # st.balloons()
        ### Insert into adatabase
        SQL = "INSERT INTO notes (name, header, note, time) VALUES(%s, %s, %s, %s);"
        data = (name, header, note, time)
        cur.execute(SQL, data)
        con.commit()

    # Previous Notes 
    st.divider()
    notes = st.checkbox("See previous notes")
    if notes:
        st.write("### **:gray[Previous Notes]**")
        cur.execute("""
                    SELECT * 
                    FROM notes
                    ORDER BY time DESC
                    """)
        for id, name, header, note, time in cur.fetchall():
            st.write(f""" \n
                    ##### :pencil: {header} \n
                    #### {note} \n
                    :man: {name} \n""")
            st.caption(f":watch: {time}")

            modify = st.toggle(f"Edit or Delete (ID #: {id})")
            if modify:
                name = st.text_input(f"Your Name (ID #: {id})", name)
                header = st.text_input(f"Header (ID #: {id})", header)
                note = st.text_area(f"Note (ID #: {id})", note)
                if st.button(f"UPDATE ID #: {id}"):
                    SQL = " UPDATE notes SET id=%s, name=%s, header=%s, note=%s WHERE id = %s"
                    data = (id, name, header, note, id)
                    cur.execute(SQL, data)
                    con.commit()
                    st.success("Successfully Edited.")
                    st.button(":blue[Done]")
                if st.button(f"DELETE ID #: {id}"):
                    cur.execute(f"DELETE FROM notes WHERE id = {id}")
                    # SQL = "DELETE FROM notes WHERE id = <...>"
                    # data = (id)
                    # cur.execute(SQL, data)
                    con.commit()
                    st.success("Successfully Deleted.")
                    st.button(":blue[Done]")
            st.subheader("",divider="gray")

    # Close Connection
    cur.close()
    con.close()
#----------End of Notepad Section----------#

#----------Counter----------#
with st.expander(' :watch: Counter'):
    st.header("Counter")
    st.caption("""
                Count every request in this app.
                """)
    st.subheader("",divider="rainbow")

    con = psycopg2.connect(f"""
                           dbname={DBNAME}
                           user={USER}
                           host={HOST}
                           port={DBPORT}
                           password={DBPASSWORD}
                           """)
    cur = con.cursor()
    # Create a table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS counter(id serial PRIMARY KEY, view int, time varchar)")
    con.commit()

    # Counter
    import time
    time = time.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
    view = 1
    ### Insert into a database
    SQL = "INSERT INTO counter (view, time) VALUES(%s, %s);"
    data = (view, time)
    cur.execute(SQL, data)
    con.commit()

    # Total views
    cur.execute("""
                SELECT SUM(view) 
                FROM counter
                """)
    st.write(f"#### Total views: **{cur.fetchone()[0]}**")
    # Current view
    st.write(f"Current: {time}")
    # Total views today
    time_date = time[0:15]
    cur.execute(f"""
                SELECT SUM(view) 
                FROM counter
                WHERE time LIKE '{time_date}%'
                """)
    st.write(f"#### Total views today: **{cur.fetchone()[0]}**")
    # Previous views
    st.divider()
    views = st.checkbox("See Previous Views")
    # TODO: Total views today (Visualization)
    if views:
        st.write("**Previous Views**")
        cur.execute("""
                    SELECT * 
                    FROM counter
                    ORDER BY time DESC
                    """)
        for _, _, time in cur.fetchall():
            st.caption(f"{time}")

    # Close Connection
    cur.close()
    con.close()
#----------End of Counter----------#


#----------External links---------#
with st.expander(' :link: External Links'):
    st.write(":link: :computer: [Personal Website](https://)")
    st.write(":link: :book: [Project Repository](https://)")
    st.write(":link: :notebook: [Blog](https://)")
    st.write(":link: :hand: [Connect with me](https://)")
#----------End of External links---------#

#----------Agent Section----------#
#----------Vertex AI----------#
st.info(":computer: :technologist: [Talk to my Agent](https://)")

#----------End of Agent Section----------#

# Close Connection
cur.close()
con.close()
#----------End of Agent Section----------#
