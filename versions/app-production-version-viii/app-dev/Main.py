#----------Import libraries----------# 
import streamlit as st
import psycopg2
import os
import time as t

#----------Database Credentials----------# 
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_HOST= os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_PASSWORD=os.getenv("DB_PASSWORD")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")
APP_PORT=os.getenv("APP_PORT")
APP_ADDRESS=os.getenv("APP_ADDRESS")
DOMAIN_NAME=os.getenv("DOMAIN_NAME")
SPECIAL_NAME=os.getenv("SPECIAL_NAME")
# Cloud Credential
PROJECT_NAME=os.getenv("PROJECT_NAME")


#----------Page Configuration----------# 
st.set_page_config(page_title="Matt Cloud Tech",
                   page_icon=":cloud:",
                   initial_sidebar_state="collapsed",
                   # menu_items={
                   #    'About':"# Matt Cloud Tech"}
                  )




def connection():
#----------Connect to a database----------#
    con = psycopg2.connect(f"""
                           dbname={DB_NAME}
                           user={DB_USER}
                           host={DB_HOST}
                           port={DB_PORT}
                           password={DB_PASSWORD}
                           """)
    cur = con.cursor()
    # Create a about table if not exists
    # cur.execute("DROP TABLE about")
    cur.execute("CREATE TABLE IF NOT EXISTS about(title varchar, about varchar, notification varchar)")
    # Create a portfolio_section table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS portfolio_section(id serial PRIMARY KEY, name varchar, portfolio varchar)")
    # Create a portfolio table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS portfolio(id serial PRIMARY KEY, project_name varchar, description varchar, link varchar)")
    # Create a message table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS messages(id serial PRIMARY KEY, email_address varchar, message varchar, time varchar)")
    # Create a notes table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS notes(id serial PRIMARY KEY, name varchar, header varchar, note varchar, time varchar)")
    # Create a counter table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS counter(id serial PRIMARY KEY, view int, time varchar)")
    con.commit()
    return con, cur

def sections(con, cur):
    #----------About Section----------#
    title = "### :cloud: Matt Cloud Tech"
    about = "##### Good day :wave:.\n##### My name is :blue[Matt]. I am a Cloud Technology Enthusiast. :technologist: \n##### Currently, I am learning and building Cloud Infrastructure, Data and CI/CD Pipelines, and Intelligent Systems."
    notification = f"###### :computer: :technologist: [:violet[Intelligent Agent] is here. Try it now. :link:](https://{DOMAIN_NAME}/Agent)"
    
    cur.execute("""
                SELECT *
                FROM about
                """)
    for title, about, notification in cur.fetchall():
        title, about, notification = title, about, notification
    st.write(title)
    st.header("", divider="rainbow")
    st.write(about)     
    st.info(notification)

    #----------Portfolio Section----------#
    with st.expander(' :notebook: Portfolio'):
        st.write("#### Project Collection")
        # Using portfolio_section table
        cur.execute("""
                    SELECT *
                    FROM portfolio_section
                    """)
        portfolio_section = "##### Project "
        name = ""
        for id, name, portfolio in cur.fetchall():
            portfolio_section = portfolio
        st.markdown(portfolio_section)
        # Manual modification
        cur.execute("""
                    SELECT * 
                    FROM portfolio
                    """)
        for id, project_name, description, link in cur.fetchall():
            st.write(f"### [{project_name}]({link})")
            st.write(f"{description}")
            st.divider()
        st.divider()
    #----------End of Portfolio Section----------#

    #----------Message Section----------#
    with st.expander(' :email: Message Me'):
        st.header(" :email: Message me",divider="rainbow")
        # Inputs
        email_address = st.text_input("Email address")
        message = st.text_area("Message")
        if st.button("Send"):
            if email_address is not "" and message is not "":
                ### Insert into adatabase
                time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
                SQL = "INSERT INTO messages (email_address, message, time) VALUES(%s, %s, %s);"
                data = (email_address, message, time)
                cur.execute(SQL, data)
                con.commit()
                st.info("Message sent")
                st.snow()
            else:
                st.info("Please add Email Address and Message before sending.")
        st.divider()
    #----------End of Message Section----------#

    #----------Notepad Section----------#
    with st.expander(' :pencil: Notepad'):
        st.header(" :pencil: Notepad",divider="rainbow")
        st.caption("""
                    Add your thoughts here. It will be stored in a database. \n
                    :warning: :red[Do not add sensitive data.]
                    """)
        # Inputs
        name = st.text_input("Your Name")
        header = st.text_input("Header")
        note = st.text_area("Note")
        import time
        if st.button("Add a note"):
            if name is not "" and header is not "" and note is not "":
                time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
                st.write(f"##### :pencil: {header} \n")
                st.text(f"{note} \n")
                st.write(f":man: {name}")
                st.caption(f":watch: {time}")
                st.info("Successfully Added.")
                st.balloons()
                ### Insert into adatabase
                SQL = "INSERT INTO notes (name, header, note, time) VALUES(%s, %s, %s, %s);"
                data = (name, header, note, time)
                cur.execute(SQL, data)
                con.commit()
            else:
                st.info("Please add Name, Header, and Note.")

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
                st.write(f"###### :pencil: {header} \n")
                st.text(f"{note} \n")
                st.write(f":man: {name}")
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
                        st.info("Successfully Edited.")
                        st.button(":blue[Done]")
                    if st.button(f"DELETE ID #: {id}"):
                        cur.execute(f"DELETE FROM notes WHERE id = {id}")
                        # SQL = "DELETE FROM notes WHERE id = <...>"
                        # data = (id)
                        # cur.execute(SQL, data)
                        con.commit()
                        st.info("Successfully Deleted.")
                        st.button(":blue[Done]")
                st.subheader("",divider="gray")
    #----------End of Notepad Section----------#

    #----------Counter----------#
    with st.expander(' :watch: Counter'):
        st.header("Counter")
        st.caption("""
                    Count every request in this app.
                    """)
        st.subheader("",divider="rainbow")
        # Counter
        time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
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
        st.divider()
    #----------End of Counter----------#


    #----------External links---------#
    with st.expander(' :link: External Links'):
        st.write(f":link: :computer: [Personal Website](https://{DOMAIN_NAME})")
        st.write(f":link: :computer: [Intelligent Agent Website](https://{DOMAIN_NAME}/Agent)")
        st.write(":link: :book: [Project Repository](https://github.com/mregojos)")
        # st.write(":link: :notebook: [Blog](https://)")
        # st.write(":link: :hand: [Connect with me](https://)")
        
        # Admin
        st.divider()
        Admin = st.checkbox("MATT CLOUD TECH")
        if Admin:
            password = st.text_input("Password", type="password")
            if password == ADMIN_PASSWORD:
                st.info("Login Success")
                option = st.text_input("About, Portfolio, Messages, Counter")
                if option == "About":
                    title= st.text_input("Title", title)
                    about = st.text_area("About", about)
                    notification = st.text_area("", notification)
                    save = st.button("Save changes")
                    if save:
                        SQL = "INSERT INTO about (title, about, notification) VALUES(%s, %s, %s);"
                        data = (title, about, notification)
                        cur.execute(SQL, data)
                        con.commit()
                        st.info("Successfully Added.")
                        st.button(":blue[Done]") 
                elif option == "Portfolio":
                    option_portfolio = st.text_input("Portfolio or Manual")
                    if option_portfolio == "Portfolio":
                        name = st.text_input("Name", name)
                        portfolio_section = st.text_area("Portfolio", portfolio_section)
                        save = st.button("Save changes")
                        if save:
                            SQL = "INSERT INTO portfolio_section (name, portfolio) VALUES(%s, %s);"
                            data = (name, portfolio_section)
                            cur.execute(SQL, data)
                            con.commit()
                            st.info("Successfully Added.")
                            st.button(":blue[Done]")                
                    elif option_portfolio == "Manual":
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
                elif option == "Messages":
                    st.info("Login success")
                    cur.execute("""
                                SELECT * 
                                FROM messages
                                """)
                    for id, email_address, message, time in cur.fetchall():
                        st.write(f"ID: {id}")
                        st.write(f"Email Address: {email_address}")
                        st.write(f"Message: {message}")
                        st.write(f"Time: {time}")
                        if st.button(f"DELETE ID #: {id}"):
                            cur.execute(f"DELETE FROM messages WHERE id = {id}")
                            con.commit()
                            st.info("Successfully Deleted.")
                            st.button(":blue[Done]")
                        st.divider()
                elif option == "Counter":
                    # Previous views
                    views = st.checkbox("See Previous Views")
                    if views:
                        st.write("**Previous Views**")
                        cur.execute("""
                                    SELECT * 
                                    FROM counter
                                    ORDER BY time DESC
                                    """)
                        for _, _, time in cur.fetchall():
                            st.caption(f"{time}")
   
    #----------End of External links---------#

    # Close Connection
    cur.close()
    con.close()


#----------Footer----------#
#----------Sidebar Footer----------#
with st.sidebar:
    st.markdown("""
                > :gray[:copyright: Portfolio Website by [Matt R.](https://github.com/mregojos)]            
                > :gray[:cloud: Deployed on [Google Cloud](https://cloud.google.com)]
                """)
    st.divider()

#----------Execution----------#
if __name__ == '__main__':
    try:
        con, cur = connection()
        sections(con, cur)
        # Close Connection
        cur.close()
        con.close()
    except:
        st.info("##### :computer: ```The app can't connect to the database right now. Please try again later.```")
    

