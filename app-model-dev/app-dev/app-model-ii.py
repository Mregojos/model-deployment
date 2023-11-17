# Development
# Version Two

# Import libraries
import streamlit as st
import psycopg2
import os
import time
import vertexai
from vertexai.language_models import TextGenerationModel
# from env import *

# Database Credentials
DBNAME=os.getenv("DBNAME") 
USER=os.getenv("USER")
HOST= os.getenv("HOST")
DBPORT=os.getenv("DBPORT")
DBPASSWORD=os.getenv("DBPASSWORD")
# Cloud
PROJECT_NAME=os.getenv("PROJECT_NAME")

#----------Page Configuration----------# 
st.set_page_config(page_title="Matt Cloud Tech",
                   page_icon=":cloud:",
                   layout="wide",
                   menu_items={
                       'About':"# Matt Cloud Tech"})

# Title
st.title("Pre-Trained Model Deployment")

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
cur.execute("CREATE TABLE IF NOT EXISTS chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, time varchar)")
con.commit()

#----------Vertex AI----------#
vertexai.init(project=PROJECT_NAME, location="us-central1")
parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison")

# response = model.predict(
#    """Hi""",
#    **parameters
# )
# st.write(f"Response from Model: {response.text}")

#----------Agent----------#
# Columns
columnA, columnB = st.columns(2)

# Column A
with columnA:
    st.header(":computer: Agent ",divider="rainbow")
    st.caption("### Chat with my agent")
    st.write(f":violet[Your chat will be stored in a database, use the same name to see your past conversations.]")
    st.caption(":warning: :red[Do not add sensitive data.]")
    input_name = st.text_input("Your Name:")
    # agent = st.toggle("**Let's go**")
    save = st.button("Save")
    if save or input_name:
        st.info(f"Your name is :blue[{input_name}]")

agent = st.toggle("**Let's go**")
prompt = ""
show = ""
if agent:
    if input_name is not "":
        prompt = st.chat_input("Talk to my agent")
        reset = st.button(":red[Reset Conversation]")
        prune = st.button(":red[Prune History]")
        if prune:
            cur.execute(f"""
                        DELETE  
                        FROM chats
                        WHERE name='{input_name}'
                        """)
            con.commit()
            st.info(f"History by {input_name} is successfully deleted.")
            
    else:
        st.info("Save your name first.")

# Column B
import time
with columnB:
    st.write("### :gray[Latest conversation]")
    if prompt:
        time = time.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
        message = st.chat_message("user")
        message.write(f":blue[{input_name}]: {prompt}")
        message.caption(f"{time}")
        message = st.chat_message("assistant")
        response = model.predict(prompt,
            **parameters
        )
        output = response.text
        message.write(output)
        message.caption(f"{time}")
        st.divider()
        

        ### Insert into a database
        SQL = "INSERT INTO chats (name, prompt, output, time) VALUES(%s, %s, %s, %s);"
        data = (input_name, prompt, output, time)
        cur.execute(SQL, data)
        con.commit()
        
        with st.expander(f"See Previous Conversation for {input_name}"):
            cur.execute(f"""
                        SELECT * 
                        FROM chats
                        WHERE name='{input_name}'
                        ORDER BY time ASC
                        """)
            for id, name, prompt, output, time in cur.fetchall():
                message = st.chat_message("user")
                message.write(f":blue[{name}]: {prompt}")
                message.caption(f"{time}")
                message = st.chat_message("assistant")
                message.write(output)
                message.caption(f"{time}")
    else:
        if not agent:
            st.info("Start the conversation now by saving your name and toggling the Let's go toggle.")
        if agent: 
            st.info("You can now start the conversation by prompting to the text bar. Enjoy. :smile:")
            with st.expander(f"See Previous Conversation for {input_name}"):
                cur.execute(f"""
                            SELECT * 
                            FROM chats
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                for id, name, prompt, output, time in cur.fetchall():
                    message = st.chat_message("user")
                    message.write(f":blue[{name}]: {prompt}")
                    message.caption(f"{time}")
                    message = st.chat_message("assistant")
                    message.write(output)
                    message.caption(f"{time}")

            

# Close Connection
cur.close()
con.close()