#----------Import libraries----------# 
import streamlit as st
import psycopg2
import os
import time
import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from vertexai.language_models import CodeChatModel

#----------Database Credentials----------# 
DBNAME=os.getenv("DBNAME") 
USER=os.getenv("USER")
HOST= os.getenv("HOST")
DBPORT=os.getenv("DBPORT")
DBPASSWORD=os.getenv("DBPASSWORD")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")
#----------Cloud Credentials----------# 
PROJECT_NAME=os.getenv("PROJECT_NAME")
vertexai.init(project=PROJECT_NAME, location="us-central1")

#----------Page Configuration----------# 
st.set_page_config(page_title="Matt Cloud Tech",
                   page_icon=":cloud:",
                   # layout="wide",
                   menu_items={
                       'About':"# Matt Cloud Tech"})

# Title
st.write("### Pre-Trained Model Deployment")

#----------Connect to a database----------# 
con = psycopg2.connect(f"""
                       dbname={DBNAME}
                       user={USER}
                       host={HOST}
                       port={DBPORT}
                       password={DBPASSWORD}
                       """)
cur = con.cursor()
# Create a table if not exists
cur.execute("CREATE TABLE IF NOT EXISTS chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar)")
cur.execute("CREATE TABLE IF NOT EXISTS guest_chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, count_prompt int)")
cur.execute("CREATE TABLE IF NOT EXISTS users(id serial PRIMARY KEY, name varchar, password varchar)")
con.commit()

#----------Vertex AI Chat----------#
chat_parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
chat_model = ChatModel.from_pretrained("chat-bison")
chat = chat_model.start_chat(
    context="""I am an agent for Matt."""
)
# response = chat.send_message("""Hi""", **chat_parameters)
# print(f"Response from Model: {response.text}")
# response = chat.send_message("""Hi""", **chat_parameters)
# print(f"Response from Model: {response.text}")

#----------Vertex AI Code----------#
code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
code_parameters = {
    "candidate_count": 1,
    "max_output_tokens": 1024,
    "temperature": 0.2
}
code_chat = code_chat_model.start_chat()
# response = code_chat.send_message("""My favorite color is white.""", **code_parameters)
# print(f"Response from Model: {response.text}")
# response = code_chat.send_message("""My favorite color is white.""", **parameters)
# print(f"Response from Model: {response.text}")

#---------Counter
# count_prompt=""
#----------Agent----------#
with st.sidebar:
    st.header(":computer: Agent ",divider="rainbow")
    st.caption("### Chat with my agent")
    # st.write("Sign-up or Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.checkbox("Stay login")
    guest = st.checkbox("Continue as a guest")
    credential = False
    # guest limit
    LIMIT = 3
    total_count= 0
#----------
    if login and guest:
        st.info("Choose only one")
#----------For Admin Login
    elif login:
        if username == "admin" and password == ADMIN_PASSWORD:
            credential = True
            st.write(f":violet[Your chat will be stored in a database, use the same name to see your past conversations.]")
            st.caption(":warning: :red[Do not add sensitive data.]")
            model = st.selectbox("Choose Chat or Code Generationt?", ('Chat', 'Code'))
            input_name = st.text_input("Your Name")
            # agent = st.toggle("**Let's go**")
            save = st.button("Save")
            if save and input_name:
                st.info(f"Your name for this conversation is :blue[{input_name}]")
            elif save and input_name == "":
                st.info("Save your name first.")
            agent = st.toggle("**:violet[Let's talk to Agent]**")
            if agent:
                if input_name is not "":
                    reset = st.button(":red[Reset Conversation]")
                    if reset:
                        st.rerun()
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
            st.info("Wrong credential")
#----------For Guest Login            
    elif guest:
        credential = True
        st.write("You will be my agent's :blue[guest].")
        st.write(f":violet[Your chat will be stored in a database, use the same name to see your past conversations.]")
        st.caption(":warning: :red[Do not add sensitive data.]")
        model = st.selectbox("Choose Chat or Code Generationt?", ('Chat', 'Code'))
        input_name = st.text_input("Your Name")
        # agent = st.toggle("**Let's go**")
        save = st.button("Save")
        if save and input_name:
            st.info(f"Your name for this conversation is :blue[{input_name}]")
        elif save and input_name == "":
            st.info("Save your name first.")
        agent = st.toggle("**:violet[Let's talk to Agent]**")
        if agent:
#----------For Guest Limit
            cur.execute(f"""
                    SELECT SUM(count_prompt)
                    FROM guest_chats
                    """)
            for total in cur.fetchone():
                if total is None:
                    total_count = 0
                    # st.write(f"{total_count}")
                else:
                    total_count = total
                    # st.write(f"{total_count}")
            if input_name is not "" and total_count < LIMIT:
                reset = st.button(":red[Reset Conversation]")
                if reset:
                    st.rerun()
                prune = st.button(":red[Prune History]")
                if prune:
                    cur.execute(f"""
                                DELETE  
                                FROM guest_chats
                                WHERE name='{input_name}'
                                """)
                    con.commit()
                    st.info(f"History by {input_name} is successfully deleted.")
        else:
            credential = False


#----------For Admin    
if login and not guest:
    if credential is False:
        st.info("Login first or continue as a guest")
    elif credential is True and agent is False:
        st.info("Save your name and toggle the :violet[Let's talk to Agent] toggle to start the conversation. Enjoy chatting :smile:")
    elif credential is True and agent is True:
        prompt_history = "Hi"
        import time
        st.write("### :gray[Start the Conversation]")
        if agent:
            prompt_user = st.chat_input("What do you want to talk about?")
            if prompt_user:
                current_time = time.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
                if model == "Chat":
                    current_model = "Chat"
                    cur.execute(f"""
                            SELECT * 
                            FROM chats
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    for id, name, prompt, output, model, time in cur.fetchall():
                        prompt_history = prompt_history + "\n " + f"{name}: {prompt}" + "\n " + f"Model Output: {output}"
                    response = chat.send_message(prompt_history, **chat_parameters)
                    response = chat.send_message(prompt_user, **chat_parameters)
                    output = response.text

                elif model == "Code":
                    current_model = "Code"
                    cur.execute(f"""
                            SELECT * 
                            FROM chats
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    for id, name, prompt, output, model, time in cur.fetchall():
                        prompt_history = prompt_history + "\n " + f"{name}: {prompt}" + "\n " + f"Model Output: {output}"
                    response = code_chat.send_message(prompt_history, **code_parameters)
                    response = code_chat.send_message(prompt_user, **code_parameters)
                    output = response.text
                    
                ### Insert into a database
                SQL = "INSERT INTO chats (name, prompt, output, model, time) VALUES(%s, %s, %s, %s, %s);"
                data = (input_name, prompt_user, output, current_model, current_time)
                cur.execute(SQL, data)
                con.commit()

                cur.execute(f"""
                SELECT * 
                FROM chats
                WHERE name='{input_name}'
                ORDER BY time ASC
                """)
                for id, name, prompt, output, model, time in cur.fetchall():
                    message = st.chat_message("user")
                    message.write(f":blue[{name}]") 
                    message.text(f"{prompt}")
                    message.caption(f"{time}")
                    message = st.chat_message("assistant")
                    message.write(output)
                    message.caption(f"{time} | Model: {model}")            

            else:
                st.info("You can now start the conversation by prompting to the text bar. Enjoy. :smile:")
                cur.execute(f"""
                SELECT * 
                FROM chats
                WHERE name='{input_name}'
                ORDER BY time ASC
                """)
                for id, name, prompt, output, model, time in cur.fetchall():
                    message = st.chat_message("user")
                    message.write(f":blue[{name}]") 
                    message.text(f"{prompt}")
                    message.caption(f"{time}")
                    message = st.chat_message("assistant")
                    message.write(output)
                    message.caption(f"{time} | Model: {model}") 
    
#----------For Guest    
elif guest and not login:
    if credential is False:
        st.info("Login first or continue as a guest")
    elif credential is True and agent is False:
        st.info("Save your name and toggle the :violet[Let's talk to Agent] toggle to start the conversation. Enjoy chatting :smile:")
    elif credential is True and agent is True and total_count < LIMIT:
        prompt_history = "Hi"
        import time
        st.write("### :gray[Start the Conversation]")
        if agent:
            prompt_user = st.chat_input("What do you want to talk about?")
            if prompt_user:
                count_prompt = 1
                current_time = time.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
                if model == "Chat":
                    current_model = "Chat"
                    cur.execute(f"""
                            SELECT * 
                            FROM guest_chats
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    for id, name, prompt, output, model, time, count_prompt in cur.fetchall():
                        prompt_history = prompt_history + "\n " + f"{name}: {prompt}" + "\n " + f"Model Output: {output}"
                    response = chat.send_message(prompt_history, **chat_parameters)
                    response = chat.send_message(prompt_user, **chat_parameters)
                    output = response.text

                elif model == "Code":
                    current_model = "Code"
                    cur.execute(f"""
                            SELECT * 
                            FROM guest_chats
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    for id, name, prompt, output, model, time, count_prompt in cur.fetchall():
                        prompt_history = prompt_history + "\n " + f"{name}: {prompt}" + "\n " + f"Model Output: {output}"
                    response = code_chat.send_message(prompt_history, **code_parameters)
                    response = code_chat.send_message(prompt_user, **code_parameters)
                    output = response.text

                ### Insert into a database
                SQL = "INSERT INTO guest_chats (name, prompt, output, model, time, count_prompt) VALUES(%s, %s, %s, %s, %s, %s);"
                data = (input_name, prompt_user, output, current_model, current_time, count_prompt)
                cur.execute(SQL, data)
                con.commit()

                cur.execute(f"""
                SELECT * 
                FROM guest_chats
                WHERE name='{input_name}'
                ORDER BY time ASC
                """)
                for id, name, prompt, output, model, time, count_prompt in cur.fetchall():
                    message = st.chat_message("user")
                    message.write(f":blue[{name}]") 
                    message.text(f"{prompt}")
                    message.caption(f"{time}")
                    message = st.chat_message("assistant")
                    message.write(output)
                    message.caption(f"{time} | Model: {model}")            

            else:
                st.info("You can now start the conversation by prompting to the text bar. Enjoy. :smile:")
                cur.execute(f"""
                SELECT * 
                FROM guest_chats
                WHERE name='{input_name}'
                ORDER BY time ASC
                """)
                for id, name, prompt, output, model, time, count_prompt in cur.fetchall():
                    message = st.chat_message("user")
                    message.write(f":blue[{name}]") 
                    message.text(f"{prompt}")
                    message.caption(f"{time}")
                    message = st.chat_message("assistant")
                    message.write(output)
                    message.caption(f"{time} | Model: {model}") 
    if total_count >= LIMIT:
        st.info("You've reached your limit.")

elif login and guest:
    st.info("Choose only one")
    
elif not login and not guest:
    st.info("Login first or continue as a guest")

#----------Close Connection----------#
cur.close()
con.close()