#----------Import libraries----------# 
import streamlit as st
import psycopg2
import os
import time as t
import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from vertexai.language_models import CodeChatModel

#----------Database Credentials----------# 
DB_NAME=os.getenv("DB_NAME") 
DB_USER=os.getenv("DB_USER")
DB_HOST= os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_PASSWORD=os.getenv("DB_PASSWORD")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")
SPECIAL_NAME=os.getenv("SPECIAL_NAME")
#----------Cloud Credentials----------# 
PROJECT_NAME=os.getenv("PROJECT_NAME")
vertexai.init(project=PROJECT_NAME, location="us-central1")

#----------Page Configuration----------# 
st.set_page_config(page_title="Matt Cloud Tech",
                   page_icon=":cloud:")

# Title
st.write("#### Pre-Trained Language Model Deployment ")

#----------Connect to a database----------# 
def connection():
    con = psycopg2.connect(f"""
                           dbname={DB_NAME}
                           user={DB_USER}
                           host={DB_HOST}
                           port={DB_PORT}
                           password={DB_PASSWORD}
                           """)
    cur = con.cursor()
    # Create a table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar)")
    cur.execute("CREATE TABLE IF NOT EXISTS guest_chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, count_prompt int)")
    # cur.execute("CREATE TABLE IF NOT EXISTS users(id serial PRIMARY KEY, name varchar, password varchar)")
    # cur.execute("DROP TABLE total_prompts")
    cur.execute("CREATE TABLE IF NOT EXISTS total_prompts(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, count_prompt int)")
    cur.execute("CREATE TABLE IF NOT EXISTS chat_view_counter(id serial PRIMARY KEY, view int, time varchar)")
    con.commit()
    return con, cur

#----------Models----------#
def models():
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
        context=f"""I am an agent for Matt."""
    )

    #----------Vertex AI Code----------#
    code_parameters = {
        "candidate_count": 1,
        "max_output_tokens": 1024,
        "temperature": 0.2
    }
    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    code_chat = code_chat_model.start_chat(
        context=f"""I am an agent for Matt."""
    )
    
    return chat, chat_parameters, code_chat, code_parameters

def sections(con, cur):
    credential = False 
    agent = False
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
        # guest daily limit
        LIMIT = 30
        total_count= 0
        # Chat View Counter
        time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
        view = 1
        SQL = "INSERT INTO chat_view_counter (view, time) VALUES(%s, %s);"
        data = (view, time)
        cur.execute(SQL, data)
        con.commit()
    #----------Login or Guest----------#
        if login and guest:
            st.info("Choose only one")
    #----------For Admin Login----------#
        elif login:
            if username == "admin" and password == ADMIN_PASSWORD:
                credential = True
                st.write(f":violet[Your chat will be stored in a database. Use the same name to see your past conversations.]")
                st.caption(":warning: :red[Do not add sensitive data.]")
                model = st.selectbox("Choose Chat or Code Generation?", ('Chat', 'Code'))
                input_name = st.text_input("Your Name")
                # agent = st.toggle("**Let's go**")
                save = st.button("Save")
                if save and input_name:
                    st.info(f"Your name for this conversation is :blue[{input_name}]")
                elif save and input_name == "":
                    st.info("Save your name first.")
                agent = st.toggle("**:violet[Start the conversation]**")
                if agent:
                    if input_name is not "":
                        # reset = st.button(":white[Refresh Conversation]")
                        # if reset:
                        #    st.rerun()
                        prune = st.button(":red[Prune History]")
                        if prune:
                            cur.execute(f"""
                                        DELETE  
                                        FROM chats
                                        WHERE name='{input_name}'
                                        """)
                            con.commit()
                            st.info(f"History by {input_name} is successfully deleted.")
                counter = st.checkbox("Counter")
                if counter:
                    st.header("Counter")
                    st.caption("""
                                Count every request in this app.
                                """)
                    st.subheader("",divider="rainbow")
                    # Total views
                    cur.execute("""
                                SELECT SUM(view) 
                                FROM chat_view_counter
                                """)
                    st.write(f"#### Total views: **{cur.fetchone()[0]}**")
                    # Current view
                    st.write(f"Current: {time}")
                    # Total views today
                    time_date = time[0:15]
                    cur.execute(f"""
                                SELECT SUM(view) 
                                FROM chat_view_counter
                                WHERE time LIKE '{time_date}%'
                                """)
                    st.write(f"#### Total views today: **{cur.fetchone()[0]}**")
                    st.divider()
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

            else:
                st.info("Wrong credential")
    #----------For Guest Login----------#            
        elif guest:
            credential = True
            st.write("You will be Agent's :blue[guest].")
            st.write(f":violet[Your chat will be stored in a database. Use the same name to see your past conversations.]")
            st.caption(":warning: :red[Do not add sensitive data.]")
            model = st.selectbox("Choose Chat or Code Generation?", ('Chat', 'Code'))
            input_name = st.text_input("Your Name")
            # agent = st.toggle("**Let's go**")
            save = st.button("Save")
            if save and input_name:
                st.info(f"Your name for this conversation is :blue[{input_name}]")
            elif save and input_name == "":
                st.info("Save your name first.")
            agent = st.toggle("**:violet[Start the conversation]**")
            time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
            time_date = time[0:15]
            if agent:
    #----------For Guest Daily Limit----------#
                cur.execute(f"""
                        SELECT SUM(count_prompt)
                        FROM guest_chats
                        WHERE time LIKE '{time_date}%'
                        """)
                for total in cur.fetchone():
                    if total is None:
                        total_count = 0
                        # st.write(f"{total_count}")
                    else:
                        total_count = total
                        # st.write(f"{total_count}")

                # if input_name is not "" and total_count < LIMIT:
                    # reset = st.button(":white[Refresh Conversation]")
                    # if reset:
                    #    st.rerun()
                # Only for Special Name
                if input_name == SPECIAL_NAME:
                    prune = st.button(":red[Prune History]")
                    if prune:
                        cur.execute(f"""
                                    DELETE  
                                    FROM guest_chats
                                    --WHERE name='{input_name}'
                                    """)
                        con.commit()
                        # st.info(f"History by {input_name} is successfully deleted.")
                        st.info(f"Prompt history is successfully deleted.")
            else:
                credential = False


    #----------For Admin----------#    
    if login and not guest:
        if credential is False:
            st.info("Save your name and toggle the :violet[Start the conversation].")
        elif credential is True and agent is False:
            st.info("Save your name and toggle the :violet[Start the conversation]. Enjoy chatting :smile:")
        elif credential is True and agent is True and input_name == "":
            st.info("Don't forget to save your name to continue.")
        elif credential is True and agent is True:
            prompt_history = "You are an intelligent Agent."
            st.write("#### :gray[Start the Conversation]")
            if agent:
                prompt_user = st.chat_input("What do you want to talk about?")
                current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
                if prompt_user:
                    count_prompt = 1
                    if model == "Chat":
                        try:
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
                            if response != " ":
                                output = response.text
                            elif response == "" or response == None:
                                output = "Oh snap. Could your repeat the prompt?"
                            else:
                                output = "Oh snap. Could your repeat the prompt?"
                            
                        except:
                            output = "Sorry for that. Could your repeat the prompt?"

                    elif model == "Code":
                        try:
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
                            if response != " ":
                                output = response.text
                            elif response == "" or response == None:
                                output = "Oh snap. Could your repeat the prompt?"
                            else:
                                output = "Oh snap. Could your repeat the prompt?"
                        except:
                            output = "I didn't catch that. Could your repeat the prompt?"

                    ### Insert into a table
                    SQL = "INSERT INTO chats (name, prompt, output, model, time) VALUES(%s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time)
                    cur.execute(SQL, data)
                    con.commit()
                    ### Insert into a table (total_prompts)
                    SQL = "INSERT INTO total_prompts (name, prompt, output, model, time, count_prompt) VALUES(%s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time, count_prompt)
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
                        message.markdown(output)
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
                        message.markdown(output)
                        message.caption(f"{time} | Model: {model}") 
                        
    #----------For Guest----------#    
    elif guest and not login:
        if credential is False:
            st.info("Save your name and toggle the :violet[Start the conversation].")
        elif credential is True and agent is False:
            st.info("Save your name and toggle the :violet[Start the conversation]. Enjoy chatting :smile:")
        elif credential is True and agent is True and input_name == "":
            st.info("Don't forget to save your name to continue.")
        elif credential is True and agent is True and total_count < LIMIT:
            prompt_history = "You are an intelligent Agent."
            import time
            st.write("#### :gray[Start the Conversation]")
            if agent:
                prompt_user = st.chat_input("What do you want to talk about?")
                current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
                if prompt_user:
                    count_prompt = 1
                    if model == "Chat":
                        try:
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
                            if response != " ":
                                output = response.text
                            elif response == "" or response == None:
                                output = "Oh snap. Could your repeat the prompt?"
                            else:
                                output = "Oh snap. Could your repeat the prompt?"
                        except:
                            output = "Sorry for that. Could your repeat the prompt?"


                    elif model == "Code":
                        current_model = "Code"
                        try:
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
                            if response != " ":
                                output = response.text
                            elif response == "" or response == None:
                                output = "Oh snap. Could your repeat the prompt?"
                            else:
                                output = "Oh snap. Could your repeat the prompt?"
                        except:
                            output = "I didn't catch that. Could your repeat the prompt?"

                    ### Insert into a database
                    SQL = "INSERT INTO guest_chats (name, prompt, output, model, time, count_prompt) VALUES(%s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time, count_prompt)
                    cur.execute(SQL, data)
                    con.commit()
                    ### Insert into a table (total_prompts)
                    SQL = "INSERT INTO total_prompts (name, prompt, output, model, time, count_prompt) VALUES(%s, %s, %s, %s, %s, %s);"
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
                        message.markdown(output)
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
                        message.markdown(output)
                        message.caption(f"{time} | Model: {model}") 
        elif total_count >= LIMIT:
            st.info("You've reached your limit.")
            
    elif login and guest:
        st.info("Choose only one")

    elif not login and not guest:
        st.info("Login first or continue as a guest")
    
   
    #----------Close Connection----------#
    cur.close()
    con.close()
    
    return credential, agent
        
        
#----------Execution----------#
if __name__ == '__main__':
    try:
        # Connection
        con, cur = connection()
        chat, chat_parameters, code_chat, code_parameters = models()
        sections(con, cur)
        # Close Connection
        cur.close()
        con.close()
    except:
        st.info("##### :computer: ```The app can't connect to the database right now. Please try again later.```")
        
    #----------Footer----------#
    #----------Sidebar Footer----------#
    with st.sidebar:
        st.markdown("""
                    ---
                    > :gray[:copyright: Portfolio Website by [Matt R.](https://github.com/mregojos)]            
                    > :gray[:cloud: Deployed on [Google Cloud](https://cloud.google.com)]
                    ---
                    """)