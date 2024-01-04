#----------Import libraries----------# 
import streamlit as st
import psycopg2
import os
import time as t
import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from vertexai.language_models import CodeChatModel
from vertexai.preview.generative_models import GenerativeModel, Part
import base64
from vertexai.preview.generative_models import GenerativeModel, Part

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
                   page_icon=":cloud:" ,
                   layout="wide")

#--------------Title----------------------#
st.write("#### Multimodal Model Deployment")

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
    
    # Multimodal
    # cur.execute("DROP TABLE multimodal")
    cur.execute("CREATE TABLE IF NOT EXISTS multimodal(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, image_detail varchar, saved_image_data_base_string varchar, total_input_characters int, total_output_characters int)")
    # cur.execute("DROP TABLE multimodal_db")
    cur.execute("CREATE TABLE IF NOT EXISTS multimodal_db(id serial PRIMARY KEY, name varchar, prompt varchar, input_prompt varchar, output varchar, output_history varchar, model varchar, time varchar, start_time float, end_time float, image_detail varchar, saved_image_data_base_string varchar, total_input_characters int, total_characters int, total_output_characters int)")
    
    # Vision
    # cur.execute("DROP TABLE vision_db")
    cur.execute("CREATE TABLE IF NOT EXISTS vision_db(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, saved_image_data_base_string varchar)")

    # Chat Text Only
    # cur.execute("DROP TABLE chats_mm")
    cur.execute("CREATE TABLE IF NOT EXISTS chats_mm(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")
    # cur.execute("DROP TABLE chats_mm_db")
    cur.execute("CREATE TABLE IF NOT EXISTS chats_mm_db(id serial PRIMARY KEY, name varchar, prompt varchar, input_prompt varchar, output varchar, output_history varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")
    # cur.execute("DROP TABLE chats")
    cur.execute("CREATE TABLE IF NOT EXISTS chats(id serial PRIMARY KEY, name varchar, prompt varchar, input_prompt varchar, output varchar, output_history varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")

    # Guest Limit
    cur.execute("CREATE TABLE IF NOT EXISTS multimodal_guest_chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, count_prompt int)")
    
    # Total Prompts
    # cur.execute("DROP TABLE total_prompts")
    cur.execute("CREATE TABLE IF NOT EXISTS total_prompts(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, count_prompt int)")
    
    # Counter
    cur.execute("CREATE TABLE IF NOT EXISTS chat_view_counter(id serial PRIMARY KEY, view int, time varchar)")
    con.commit()
    return con, cur

#----------Models----------#
def models():
    #----------Gemini Pro---------------#
    mm_config = {
        "max_output_tokens": 2048,
        "temperature": 0.2,
        "top_p": 1
    }
    mm_model = GenerativeModel("gemini-pro")
    mm_chat = mm_model.start_chat()
    # print(mm_chat.send_message("""Hi. I'm Matt.""", generation_config=mm_config))
    
    #----------Gemini Pro Vision---------------#
    multimodal_model = GenerativeModel("gemini-pro-vision")
    multimodal_generation_config = {
        "max_output_tokens": 2048,
        "temperature": 0.2,
        "top_p": 1,
        "top_k": 32
    }
    
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
        # context=f"""I am an intelligent agent."""
    )

    #----------Vertex AI Code----------#
    code_parameters = {
        "candidate_count": 1,
        "max_output_tokens": 1024,
        "temperature": 0.2
    }
    code_chat_model = CodeChatModel.from_pretrained("codechat-bison")
    code_chat = code_chat_model.start_chat(
        # context=f"""I am an intelligent agent."""
    )
    

    return mm_config, mm_chat, multimodal_model, multimodal_generation_config, chat, chat_parameters, code_chat, code_parameters


#----------- Multimodal, Chat, Multimodal with Database, Vision (One-Turn), Vision with DB, Chat with DB --------------#
def multimodal(con, cur):    
    #----------------- Variables ------------------------#
    total_prompt = 0
    button = False
    prompt_user_chat = None
    button_streaming = False
    model = ""
    total_prompt_limit = 4
    count_prompt = 1
    round_number = 2
    number_columns = 2
    character_limit = 10000
    character_limit_w = "ten thousand characters"
    output = ""
    current_model = ""
    prompt_character_limit = 5000 # Only Applicable to Guest
    prompt_character_limit_text = f""":red[CHARACTER LIMIT]: Exceeds the prompt character limit of :blue[{prompt_character_limit}]""" 
    
    #------------------ Admin --------------------------#
    with st.sidebar:
        if GUEST == False:
            input_name = st.text_input("Name", default_name)

    #------------------ Guest Counter ------------------#
    if GUEST == True:
        input_name = default_name
    LIMIT = 2
    time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
    time_date = time[0:15]
    cur.execute(f"""
            SELECT SUM(count_prompt)
            FROM multimodal_guest_chats
            WHERE time LIKE '{time_date}%'
            """)
    for total in cur.fetchone():
        if total is None:
            total_count = 0
        else:
            total_count = total
            # st.write(total_count)
    
    #------------------ Info and Sample prompts  --------------------------#
    # if GUEST == False or (GUEST == True and total_count < LIMIT):
    info_sample_prompts = """
                You can now start the conversation by prompting in the text bar. Enjoy. :smile: You can ask:
                * What is Cloud Computing?
                * What is Google Cloud?
                * Important Google Cloud Services to know
                * Compare Site Reliability Engineering with DevOps
                * Tell me about different cloud services
                * Explain Cloud Computing in simple terms
                * Tell me a funny quote related to Cloud Computing
                """
    vision_info_ = """
                You can now upload an image to analyze.
                """
    
    with st.sidebar:
        #------------------ Prompt starts --------------------------#
        if (GUEST == False) or (GUEST == True and total_count < LIMIT): 
            model = st.selectbox("Choose Model", (["Multimodal (One-Turn)", "Multimodal", "Multimodal (Multi-Turn)", "Multimodal with DB", "Vision (One-Turn)", "Vision (One-Turn) with DB", "Text Only (One-Turn)",  "Chat Text Only", "Chat Text Only (Multi-Turn)", "Chat Text Only with DB", "Chat Text Only (Latest vs Old Version)", "Chat Text Only (Old Version)", "Code (Old Version)" ]))
            prompt_user = st.text_area("Prompt")                
            uploaded_file = None
            current_image_detail = ""
            image_data_base_string = ""
            current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")

        #------------------ prompt_info ------------------#
        prompt_history = "You are an intelligent Agent."
        
        multimodal_info = f":violet[{model}  Model]. This model stores prompt history only."
        multimodal_four_turn_info = f"For :violet[{model} Model], chat history (short-term memory) is purposely limited to four prompts only. :red[Prune history] to clear the previous prompts or use other models."
        multimodal_db_info = f":violet[{model}] Memory is limited to {character_limit_w} only. Once it reaches the limit, all data in the memory will be deleted, but the prompt history can still be viewed in the conversation."
        vision_info = f":violet[{model}] analyzes the photo you uploaded."
        vision_db_info = f":violet[{model}] analyzes the photo you uploaded and saves to the database. This model does not have chat capability."
        chat_info = f":violet[{model}  Model]. This model stores prompt history only."
        chat_four_turn_info = f"For :violet[{model} Model], chat history (short-term memory) is purposely limited to four prompts only. :red[Prune history] to clear the previous prompts or use other models."
        chat_db_info = f":violet[{model}] Memory is limited to {character_limit_w} only. Once it reaches the limit, all data in the memory will be deleted, but the prompt history can still be viewed in the conversation."
        chat_latest_old_info = f":violet[{model}] shows and compares the latest model to the old model version."
        chat_old_info = f":violet[{model}] Memory is limited to {character_limit_w} only. Once it reaches the limit, all data in the memory will be deleted, but the prompt history can still be viewed in the conversation."
        code_old_info = f":violet[{model}] Memory is limited to {character_limit_w} only. Once it reaches the limit, all data in the memory will be deleted, but the prompt history can still be viewed in the conversation."
        
        prompt_prune_info = f"Prompt history by {input_name} was successfully deleted."
        prompt_error = "Sorry about that. Please prompt it again, prune the history, or change the model if the issue persists."
        prompt_user_chat_ = "What do you want to talk about?"

    #------------------ Guest limit --------------------------#
    if GUEST == True and total_count >= LIMIT:
        with st.sidebar:
            st.info("Guest daily limit has been reached.")

            # If the limit is reached, this will automatically delete all Guest prompt history. Note: "multimodal_guest_chats" is not included.
            guest_DB = ["multimodal", "multimodal_db", "vision_db", "chats_mm", "chats_mm_db", "chats"]
            for DB in guest_DB:
                cur.execute(f"DROP TABLE {DB}")
            con.commit()
            
        st.info("Guest daily limit has been reached.")

    #-------------------Conversation starts here---------------------#
    #-------------------Multimodal (One-Turn)---------------------#
    if model == "Multimodal (One-Turn)":
        current_model = "Multimodal (One-Turn)"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
        input_characters = ""
        end_time = ""
        OUTPUT = False
        with st.sidebar:
            image = st.checkbox("Add a photo")
            if image:
                uploaded_file = st.file_uploader("Upload a photo", type=["png"])
                if uploaded_file is not None:
                    image_data = uploaded_file.read()
                    image_name = uploaded_file.name
                    st.image(image_data, image_name)
                    image_data_base = base64.b64encode(image_data)
                    image_data_base_string = base64.b64encode(image_data).decode("utf-8")
                    # image_data_base_string_data = base64.b64decode(image_data_base_string)
                    # st.image(image_data_base_string_data)
                    image = Part.from_data(data=base64.b64decode(image_data_base), mime_type="image/png")
                    responses = multimodal_model.generate_content(["Explain the image in detail", image], generation_config=multimodal_generation_config)
                    current_image_detail = responses.text
                else:
                    image_data_base_string = ""
            
            
            button = st.button("Generate")
            button_streaming = st.button("Generate (Streaming)")
            current_start_time = t.time() 
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    OUTPUT = True
                    try:
                        if uploaded_file is not None:
                            response = mm_chat.send_message(f"{prompt_user}. I add an image: {current_image_detail}"  , generation_config=mm_config)
                            output = response.text
                        if uploaded_file is None:
                            response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                            output = response.text
                    except:
                        output = prompt_error
                    input_characters = len(prompt_user)
                    output_characters = len(output)
                    end_time = t.time() 
                      
            response = ""
            response_ = ""
            if button_streaming:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    OUTPUT = True
                    current_start_time = t.time() 
                    try:
                        if uploaded_file is not None:
                            response = mm_chat.send_message(f"{prompt_user}. I add an image: {current_image_detail}"  , stream=True, generation_config=mm_config)
                        if uploaded_file is None:
                            response = mm_chat.send_message(prompt_user, stream=True, generation_config=mm_config)
                    except:
                        output = prompt_error

                input_characters = len(prompt_user)
                
            # st.info(multimodal_info)
            
            refresh = st.button(":blue[Reset]")
            if refresh:
                st.rerun()
                
        if (button or prompt_user_chat) and OUTPUT == True:
            message = st.chat_message("user")
            message.write(f":blue[{input_name}]") 
            if uploaded_file is not None:
                message.image(image_data, image_name)
                message.text(f"{prompt_user}")
                message.caption(f"{current_time} | Input Characters: {input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output)
                message.caption(f"{current_time} | Model: {current_model} | Processing Time: {round(end_time-current_start_time, round_number)} seconds | Output Characters: {output_characters}" ) 
            elif uploaded_file is None:
                message.text(f"{prompt_user}")
                message.caption(f"{current_time} | Input Characters: {input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output)
                message.caption(f"{current_time} | Model: {current_model} | Processing Time: {round(end_time-current_start_time, round_number)} seconds | Output Characters: {output_characters}")

        elif button_streaming and OUTPUT == True:
            message = st.chat_message("user")
            message.write(f":blue[{input_name}]") 
            if uploaded_file is not None:
                message.image(image_data, image_name)
                message.text(f"{prompt_user}")
                message.caption(f"{current_time} | Input Characters: {input_characters}")
                message = st.chat_message("assistant")
                for chunk in response:
                    message.markdown(chunk.text)
                    response_ = response_ + chunk.text 
                output_characters = len(response_)
                end_time = t.time()
                message.caption(f"{current_time} | Model: {current_model} | Processing Time: {round(end_time-current_start_time, round_number)} seconds | Output Characters: {output_characters}" ) 
            elif uploaded_file is None:
                message.text(f"{prompt_user}")
                message.caption(f"{current_time} | Input Characters: {input_characters}")
                message = st.chat_message("assistant")
                for chunk in response:
                    message.markdown(chunk.text)
                    response_ = response_ + chunk.text 
                output_characters = len(response_)
                end_time = t.time() 
                message.caption(f"{current_time} | Model: {current_model} | Processing Time: {round(end_time-current_start_time, round_number)} seconds | Output Characters: {output_characters}")

        
        model = "Multimodal (One-Turn)"
        
    #-------------------Multimodal---------------------#
    # It stores the prompts only
    if model == "Multimodal":
        current_model = "Multimodal"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        with st.sidebar:
            image = st.checkbox("Add a photo")
            if image:
                uploaded_file = st.file_uploader("Upload a photo", type=["png"])
                if uploaded_file is not None:
                    image_data = uploaded_file.read()
                    image_name = uploaded_file.name
                    st.image(image_data, image_name)
                    image_data_base = base64.b64encode(image_data)
                    image_data_base_string = base64.b64encode(image_data).decode("utf-8")
                    # image_data_base_string_data = base64.b64decode(image_data_base_string)
                    # st.image(image_data_base_string_data)
                    image = Part.from_data(data=base64.b64decode(image_data_base), mime_type="image/png")
                    responses = multimodal_model.generate_content(["Explain the image in detail", image], generation_config=multimodal_generation_config)
                    current_image_detail = responses.text
                else:
                    image_data_base_string = ""
            
            current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
            button = st.button("Send")
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time() 
                    cur.execute(f"""
                            SELECT * 
                            FROM multimodal
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    try:
                        for id, name, prompt, output, model, time, start_time, end_time, image_detail, saved_image_data_base_string, total_input_characters, total_output_characters in cur.fetchall():
                            prompt_history = f"""{prompt_history}
                                             \n prompt {id}: {prompt} 
                                              """
                        if prompt_history != "":
                            response = mm_chat.send_message(prompt_history, generation_config=mm_config)
                        if uploaded_file is not None:
                            response = mm_chat.send_message(f"{prompt_user}. I add an image: {current_image_detail}"  , generation_config=mm_config)
                            output = response.text
                        if uploaded_file is None:
                            response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                            output = response.text
                    except:
                        output = prompt_error

                    input_characters = len(prompt_user)
                    output_characters = len(output)
                    end_time = t.time() 
                    SQL = "INSERT INTO multimodal (name, prompt, output, model, time, start_time, end_time, saved_image_data_base_string, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, image_data_base_string, input_characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit()
                    
            st.info(multimodal_info)
            
            prune = st.button(":red[Prune History]")
            if prune:
                # cur.execute(f"""
                #            DELETE  
                #            FROM multimodal
                #            WHERE name='{input_name}'
                #            """)
                cur.execute("DROP TABLE multimodal")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
                
        cur.execute(f"""
        SELECT * 
        FROM multimodal
        WHERE name='{input_name}'
        ORDER BY time ASC
        """)
        for id, name, prompt, output, model, time, start_time, end_time, image_detail, saved_image_data_base_string, total_input_characters, total_output_characters in cur.fetchall():
            message = st.chat_message("user")
            message.write(f":blue[{name}]") 
            if saved_image_data_base_string is not "":
                image_data_base_string_data = base64.b64decode(saved_image_data_base_string)
                message.image(image_data_base_string_data)
                message.text(f"{prompt}")
                message.caption(f"{time} | Input Characters: {total_input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output)
                message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}" )                 
            elif saved_image_data_base_string is "":
                message.text(f"{prompt}")
                message.caption(f"{time} | Input Characters: {total_input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output)
                message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}")
        model = "Multimodal"
        
    #-------------------Multimodal (Multi-Turn)---------------------#
    if model == "Multimodal (Multi-Turn)":
        current_model = "Multimodal (Multi-Turn)"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input("What do you want to talk about? ")
        with st.sidebar:
            image = st.checkbox("Add a photo")
            if image:
                uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    image_data = uploaded_file.read()
                    image_name = uploaded_file.name
                    st.image(image_data, image_name)
                    image_data_base = base64.b64encode(image_data)
                    image_data_base_string = base64.b64encode(image_data).decode("utf-8")
                    # image_data_base_string_data = base64.b64decode(image_data_base_string)
                    # st.image(image_data_base_string_data)
                    image = Part.from_data(data=base64.b64decode(image_data_base), mime_type="image/png")
                    responses = multimodal_model.generate_content(["Explain the image in detail", image], generation_config=multimodal_generation_config)
                    current_image_detail = responses.text
                else:
                    image_data_base_string = ""
            # video = st.checkbox("Add a video")
            # if video:
            #     pass
            
            # Four prompts (short-memory) only
            cur.execute(f"""
                SELECT COUNT(*) 
                FROM multimodal
                WHERE name='{input_name}'
                """)
            total_prompt =cur.fetchone()[0]
            if total_prompt <= total_prompt_limit:
                if total_prompt < total_prompt_limit: 
                    button = True
                    button = st.button("Send")
                elif total_prompt >= total_prompt_limit:
                    button = False
                    prompt_user_chat = False
                    
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time() 
                    cur.execute(f"""
                            SELECT * 
                            FROM multimodal
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    try:
                        for id, name, prompt, output, model, time, start_time, end_time, image_detail, saved_image_data_base_string, total_input_characters, total_output_characters in cur.fetchall():
                            response = mm_chat.send_message(prompt, generation_config=mm_config)
                        if uploaded_file is not None:
                            response = mm_chat.send_message(f"{prompt_user}. I add an image: {current_image_detail}"  , generation_config=mm_config)
                            output = response.text
                        else:
                            response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                            output = response.text
                    except:
                        output = prompt_error

                    input_characters = len(prompt_user)
                    output_characters = len(output)
                    end_time = t.time() 
                    SQL = "INSERT INTO multimodal (name, prompt, output, model, time, start_time, end_time, saved_image_data_base_string, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, image_data_base_string, input_characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit()
                    
            st.info(multimodal_four_turn_info)
            
            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE multimodal")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
                
        cur.execute(f"""
        SELECT * 
        FROM multimodal
        WHERE name='{input_name}'
        ORDER BY time ASC
        """)
        for id, name, prompt, output, model, time, start_time, end_time, image_detail, saved_image_data_base_string, total_input_characters, total_output_characters in cur.fetchall():
            message = st.chat_message("user")
            message.write(f":blue[{name}]") 
            if saved_image_data_base_string is not "":
                image_data_base_string_data = base64.b64decode(saved_image_data_base_string)
                message.image(image_data_base_string_data)
                message.text(f"{prompt}")
                message.caption(f"{time} | Input Characters: {total_input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output)
                message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}" )                 
            elif saved_image_data_base_string is "":
                message.text(f"{prompt}")
                message.caption(f"{time} | Input Characters: {total_input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output)
                message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}")
        model = "Multimodal (Multi-Turn)"
        
    #-------------------Multi-Modal with DB---------------------#
    if model == "Multimodal with DB":
        current_model = "Multimodal with DB"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        with st.sidebar:
            #-------------------Multimodal with DB---------------------#
            uploaded_file = None
            current_image_detail = ""
            image_data_base_string = ""
            image = st.checkbox("Add a photo")
            if image:
                uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    image_data = uploaded_file.read()
                    image_name = uploaded_file.name
                    st.image(image_data, image_name)
                    image_data_base = base64.b64encode(image_data)
                    image_data_base_string = base64.b64encode(image_data).decode("utf-8")
                    # image_data_base_string_data = base64.b64decode(image_data_base_string)
                    # st.image(image_data_base_string_data)
                    image = Part.from_data(data=base64.b64decode(image_data_base), mime_type="image/png")
                    responses = multimodal_model.generate_content(["Explain the image in detail", image], generation_config=multimodal_generation_config)
                    current_image_detail = responses.text
                else:
                    image_data_base_string = ""
            # video = st.checkbox("Add a video")
            # if video:
            #     pass

            current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
            button = st.button("Send")
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time() 
                    
                    cur.execute(f"""
                            SELECT * 
                            FROM multimodal_db
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    try:
                        for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, image_detail, saved_image_data_base_string, total_input_characters, total_characters, total_output_characters in cur.fetchall():
                            prompt_history = f"""
                                             \n {name}: {prompt} 
                                             \n Model Output: {output}
                                             \n ------------
                                             \n
                                              """

                        response = mm_chat.send_message(prompt_history, generation_config=mm_config)
                        if uploaded_file is not None:
                            response = mm_chat.send_message(f"{prompt_user}. I add an image: {current_image_detail}"  , generation_config=mm_config)
                            output = response.text
                        else:
                            response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                            output = response.text
                    except:
                        output = prompt_error
                    # Print out expection
                    # except Exception as e:
                    #    with st.sidebar:
                    #        st.write(f"Exception: {e}")
                    #    output = "Sorry about that. Please prompt it again."

                    ### Insert into a table
                    input_characters = len(prompt_user)
                    characters = len(prompt_history)
                    output_characters = len(output)
                    end_time = t.time() 
                    SQL = "INSERT INTO multimodal_db (name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, saved_image_data_base_string, total_input_characters, total_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, prompt_user, output, output, current_model, current_time, current_start_time, end_time, image_data_base_string, input_characters, characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit()

                    # For Character limit
                    if characters >= character_limit:
                        cur.execute(f"""
                                    UPDATE multimodal_db
                                    SET prompt=NULL
                                    """)
                        cur.execute(f"""
                                    UPDATE multimodal_db
                                    SET output=NULL
                                    """)
                        con.commit()
                        
            st.info(multimodal_db_info)
                    # st.write(characters)

            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE multimodal_db")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
                    
        cur.execute(f"""
        SELECT * 
        FROM multimodal_db
        WHERE name='{input_name}'
        ORDER BY time ASC
        """)
        for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, image_detail, saved_image_data_base_string, total_input_characters, total_characters, total_output_characters in cur.fetchall():
            message = st.chat_message("user")
            message.write(f":blue[{name}]") 
            if saved_image_data_base_string is not "":
                image_data_base_string_data = base64.b64decode(saved_image_data_base_string)
                message.image(image_data_base_string_data)
                message.text(f"{input_prompt}")
                message.caption(f"{time} | Input Characters: {total_input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output_history)
                message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}" )
            else:
                message.text(f"{input_prompt}")
                message.caption(f"{time} | Input Characters: {total_input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output_history)
                message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}")
        model = "Multimodal with DB"

    #-------------------Vision---------------------#
    if model == "Vision (One-Turn)":
        current_model = "Vision (One-Turn)"
        st.info(vision_info_)
        with st.sidebar:
            if prompt_user == "":
                prompt_user = "What is the image? Tell me more about the image."   
            image = st.checkbox("Add a photo")
            try:
                if image:
                    uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
                    if uploaded_file is not None:
                        image_data = uploaded_file.read()
                        image_name = uploaded_file.name
                        st.image(image_data, image_name)
                        image_data_base = base64.b64encode(image_data)
                        image_data_base_string = base64.b64encode(image_data).decode("utf-8")
                        # image_data_base_string_data = base64.b64decode(image_data_base_string)
                        # st.image(image_data_base_string_data)
                        image = Part.from_data(data=base64.b64decode(image_data_base), mime_type="image/png")
                start_time = t.time() 
                button = st.button("Send")
                if button:
                    if (len(prompt_user) >= prompt_character_limit) and GUEST:
                        st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                    if uploaded_file is None:
                        st.info("Upload file first")
                    if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                        responses = multimodal_model.generate_content([prompt_user, image], generation_config=multimodal_generation_config)
                        output = responses.text
                        end_time = t.time()
            except:
                output = prompt_error
                end_time = t.time()
                
            st.info(vision_info)
                    
        if uploaded_file is not None and button:
            message = st.chat_message("assistant")
            message.image(image_data)
            message.markdown(output)
            message.caption(f"{current_time} | Model: {current_model} | Processing Time: {round(end_time-start_time, round_number)} seconds")

    #-------------------Vision with DB--------------------#
    if model == "Vision (One-Turn) with DB":
        current_model = "Vision (One-Turn) with DB"
        # Vision (One-Turn) with Database only; No memory of the past conversations.
        st.info(vision_info_)
        with st.sidebar:
            if prompt_user == "":
                prompt_user = "What is the image? Tell me more about the image."  
            image = st.checkbox("Add a photo")
            if image:
                uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
                if uploaded_file is not None:
                    image_data = uploaded_file.read()
                    image_name = uploaded_file.name
                    st.image(image_data, image_name)
                    image_data_base = base64.b64encode(image_data)
                    image_data_base_string = base64.b64encode(image_data).decode("utf-8")
                    # image_data_base_string_data = base64.b64decode(image_data_base_string)
                    # st.image(image_data_base_string_data)
                    image = Part.from_data(data=base64.b64decode(image_data_base), mime_type="image/png")            
            button = st.button("Send")
            if button:
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if uploaded_file is None:
                    st.info("Upload file first")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time() 
                    cur.execute(f"""
                            SELECT * 
                            FROM vision_db
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    try: 
                        for id, name, prompt, output, model, time, start_time, end_time, saved_image_data_base_string in cur.fetchall():
                            if saved_image_data_base_string is not None:
                                image_data_base_string_data = base64.b64decode(saved_image_data_base_string)
                                image_data_base = base64.b64encode(image_data_base_string_data)
                                saved_image = Part.from_data(data=base64.b64decode(image_data_base), mime_type="image/png")       
                                responses = multimodal_model.generate_content([prompt, saved_image], generation_config=multimodal_generation_config)
                            else:
                                responses = multimodal_model.generate_content(prompt, generation_config=multimodal_generation_config)
                        if uploaded_file is not None:
                            responses = multimodal_model.generate_content([prompt_user, image], generation_config=multimodal_generation_config)
                            output = responses.text
                            end_time = t.time()
                        else:
                            responses = multimodal_model.generate_content(prompt_user, generation_config=multimodal_generation_config)
                            output = responses.text
                    except:
                            responses = multimodal_model.generate_content(prompt_user, generation_config=multimodal_generation_config)
                            output = responses.text
                            
                    ### Insert into a table
                    SQL = "INSERT INTO vision_db (name, prompt, output, model, time, start_time, end_time, saved_image_data_base_string) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, image_data_base_string)
                    cur.execute(SQL, data)
                    con.commit()
            
            st.info(vision_db_info)

            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE vision_db")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
                
        cur.execute(f"""
        SELECT * 
        FROM vision_db
        WHERE name='{input_name}'
        ORDER BY time ASC
        """)
        for id, name, prompt, output, model, time, start_time, end_time, saved_image_data_base_string in cur.fetchall():
            message = st.chat_message("assistant")
            if saved_image_data_base_string is not None:
                image_data_base_string_data = base64.b64decode(saved_image_data_base_string)
                message.image(image_data_base_string_data)
            message.markdown(output)
            message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds")
            
    #------------------- Text Only (One-Turn)---------------------#
    if model == "Text Only (One-Turn)":
        current_model = "Text Only (One-Turn)"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
        input_characters = ""
        end_time = ""
        OUTPUT = False
        with st.sidebar:
            button = st.button("Generate")
            button_streaming = st.button("Generate (Streaming)")
            current_start_time = t.time() 
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    OUTPUT = True
                    try:
                        response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                        output = response.text
                    except:
                        output = prompt_error
                    input_characters = len(prompt_user)
                    output_characters = len(output)
                    end_time = t.time() 
                      
            response_ = ""
            if button_streaming:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    OUTPUT = True
                    current_start_time = t.time() 
                    try:
                        response = mm_chat.send_message(prompt_user, stream=True, generation_config=mm_config)
                    except:
                        output = prompt_error

                input_characters = len(prompt_user)
                
            # st.info(multimodal_info)
            
            refresh = st.button(":blue[Reset]")
            if refresh:
                st.rerun()
                
        if (button or prompt_user_chat) and OUTPUT == True:
            message = st.chat_message("user")
            message.write(f":blue[{input_name}]") 
            message.text(f"{prompt_user}")
            message.caption(f"{current_time} | Input Characters: {input_characters}")
            message = st.chat_message("assistant")
            message.markdown(output)
            message.caption(f"{current_time} | Model: {current_model} | Processing Time: {round(end_time-current_start_time, round_number)} seconds | Output Characters: {output_characters}")

        elif button_streaming and OUTPUT == True:
            message = st.chat_message("user")
            message.write(f":blue[{input_name}]") 
            message.text(f"{prompt_user}")
            message.caption(f"{current_time} | Input Characters: {input_characters}")
            message = st.chat_message("assistant")
            for chunk in response:
                message.markdown(chunk.text)
                response_ = response_ + chunk.text 
            output_characters = len(response_)
            end_time = t.time() 
            # message.markdown(output)
            message.caption(f"{current_time} | Model: {current_model} | Processing Time: {round(end_time-current_start_time, round_number)} seconds | Output Characters: {output_characters}")

        
        model = "Text Only (One-Turn)"

    #-------------------Chat Text Only---------------------#
    if model == "Chat Text Only":
        current_model = "Chat Text Only"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        with st.sidebar:
            current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
            button = st.button("Send")
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time() 
                    cur.execute(f"""
                            SELECT * 
                            FROM chats_mm
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)                    
                    try:
                        for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                            prompt_history = f"""{prompt_history}
                                             \n prompt {id}: {prompt} 
                                              """
                        if prompt_history != "":
                            response = mm_chat.send_message(prompt_history, generation_config=mm_config)
                        response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                        output = response.text
                    except:
                        output = prompt_error

                    output_characters = len(output)
                    characters = len(prompt_user)
                    end_time = t.time() 
                    SQL = "INSERT INTO chats_mm (name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit() 
                    
            st.info(chat_info) 
            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE chats_mm")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
                    
        cur.execute(f"""
        SELECT * 
        FROM chats_mm
        WHERE name='{input_name}'
        ORDER BY time ASC
        """)
        for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
            message = st.chat_message("user")
            message.write(f":blue[{name}]") 
            message.text(f"{prompt}")
            message.caption(f"{time} | Input Characters: {total_input_characters}")
            message = st.chat_message("assistant")
            message.markdown(output)
            message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}")
            
        model = "Chat Text Only"
            
    #-------------------Chat Text Only (Multi-Turn)---------------------#
    if model == "Chat Text Only (Multi-Turn)":
        current_model = "Chat Text Only (Multi-Turn)"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        with st.sidebar:
            # Four prompts (short-memory) only
            cur.execute(f"""
                SELECT COUNT(*) 
                FROM chats_mm
                WHERE name='{input_name}'
                """)
            total_prompt =cur.fetchone()[0]
            if total_prompt <= total_prompt_limit:
                if total_prompt < total_prompt_limit: 
                    button = True 
                    button = st.button("Send")
                elif total_prompt >= total_prompt_limit:
                    button = False
                    prompt_user_chat = False
                    
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time() 
                    cur.execute(f"""
                            SELECT * 
                            FROM chats_mm
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)                    
                    try:
                        for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                            response = mm_chat.send_message(prompt, generation_config=mm_config)
                        response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                        output = response.text
                    except:
                        output = prompt_error

                    output_characters = len(output)
                    characters = len(prompt_user)
                    end_time = t.time() 
                    SQL = "INSERT INTO chats_mm (name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit()       

            st.info(chat_four_turn_info) 
            
            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE chats_mm")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
                    
        cur.execute(f"""
        SELECT * 
        FROM chats_mm
        WHERE name='{input_name}'
        ORDER BY time ASC
        """)
        for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
            message = st.chat_message("user")
            message.write(f":blue[{name}]") 
            message.text(f"{prompt}")
            message.caption(f"{time} | Input Characters: {total_input_characters}")
            message = st.chat_message("assistant")
            message.markdown(output)
            message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}")
            
        model = "Chat Text Only (Multi-Turn)"
        
    #-------------------Chat Text Only with DB---------------------#
    if model == "Chat Text Only with DB":
        current_model = "Chat Text Only with DB"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        with st.sidebar:
            button = st.button("Send")
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time() 
                    cur.execute(f"""
                            SELECT * 
                            FROM chats_mm_db
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)            
                    for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                        prompt_history = f"""
                                             \n ------------
                                             \n {name}: {prompt} 
                                             \n Model Output: {output}
                                             \n ------------
                                             \n
                                              """
                    try:
                        response = mm_chat.send_message(prompt_history, generation_config=mm_config)
                        response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                        if response != " ":
                            output = response.text
                        elif response == "" or response == None:
                            output = prompt_error
                        else:
                            output = prompt_error
                    except:
                        output = prompt_error
         
                    characters = len(prompt_history + prompt_user)
                    input_characters = len(prompt_user)
                    output_characters = len(output)
                    end_time = t.time()
                    SQL = "INSERT INTO chats_mm_db (name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, prompt_user, output, output, current_model, current_time, current_start_time, end_time, input_characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit()

                    # For Character limit
                    if characters >= character_limit:
                        cur.execute(f"""
                                    UPDATE chats_mm_db
                                    SET prompt=NULL
                                    """)
                        cur.execute(f"""
                                    UPDATE chats_mm_db
                                    SET output=NULL
                                    """)
                        con.commit()
                    # st.write(characters)
                        
            st.info(chat_db_info)

            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE chats_mm_db")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
                    
        cur.execute(f"""
        SELECT * 
        FROM chats_mm_db
        WHERE name='{input_name}'
        ORDER BY time ASC
        """)
        for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
            message = st.chat_message("user")
            message.write(f":blue[{name}]") 
            message.text(f"{input_prompt}")
            message.caption(f"{time} | Input Characters: {total_input_characters}")
            message = st.chat_message("assistant")
            message.markdown(output_history)
            message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}")
            
    #-------------------Comparison: Chat Text Only (Latest vs Old Version)---------------------------------------#
    if model == "Chat Text Only (Latest vs Old Version)":
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        prompt_history = ""
        with st.sidebar:
            button = st.button("Send")
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    #-------------------Chat Text Only Latest Version---------------------#
                    current_start_time = t.time() 
                    current_model = "Latest Version"
                    cur.execute(f"""
                            SELECT * 
                            FROM chats_mm
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)                    
                    try:
                        for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                            prompt_history = f"""{prompt_history}
                                             \n prompt {id}: {prompt} 
                                              """
                        if prompt_history != "":
                            response = mm_chat.send_message(prompt_history, generation_config=mm_config)
                        response = mm_chat.send_message(prompt_user, generation_config=mm_config)
                        output = response.text
                    except:
                        output = prompt_error

                    output_characters = len(output)
                    characters = len(prompt_user)
                    end_time = t.time() 
                    SQL = "INSERT INTO chats_mm (name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit() 

                    #-------------------Chat Only Old Version---------------------#
                    current_start_time = t.time()
                    current_model = "Old Version"
                    cur.execute(f"""
                            SELECT * 
                            FROM chats
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """) 
                    for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                        prompt_history = f"""{prompt_history}
                                          \n prompt {id}: {prompt} 
                                          """
                    try:
                        if prompt_history != "":
                            response = chat.send_message(prompt_history, **chat_parameters)
                        response = chat.send_message(prompt_user, **chat_parameters)
                        output = response.text 
                    except:
                        output = prompt_error

                    characters = len(prompt_history + prompt_user)
                    input_characters = len(prompt_user)
                    output_characters = len(output)
                    end_time = t.time()
                    SQL = "INSERT INTO chats (name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, prompt_user, output, output, current_model, current_time, current_start_time, end_time, input_characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit()
                    
            st.info(chat_latest_old_info)
            
            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE chats_mm")
                cur.execute("DROP TABLE chats")
                con.commit()
                st.rerun()
                st.info(prompt_prune_info)
                
        col_A, col_B = st.columns(number_columns)
        
        with col_A:
            #-------------------Chat Text Only Latest Version---------------------#
            cur.execute(f"""
            SELECT * 
            FROM chats_mm
            WHERE name='{input_name}'
            ORDER BY time ASC
            """)
            for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                message = st.chat_message("user")
                message.write(f":blue[{name}]") 
                message.text(f"{prompt}")
                message.caption(f"{time} | Input Characters: {total_input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output)
                message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}")
            model = "Latest Version"
        
        with col_B:
            #-------------------Chat Only Old Version---------------------#
            cur.execute(f"""
            SELECT * 
            FROM chats
            WHERE name='{input_name}'
            ORDER BY time ASC
            """)
            for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                message = st.chat_message("user")
                message.write(f":blue[{name}]") 
                message.text(f"{input_prompt}")
                message.caption(f"{time} | Input Characters: {total_input_characters}")
                message = st.chat_message("assistant")
                message.markdown(output_history)
                message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}") 
            model = "Old Version"

    #-------------------Old Version---------------------------------#
    #-------------------Chat Only (Old Version)---------------------#
    if model == "Chat Text Only (Old Version)":
        current_model = "Chat Text Only (Old Version)"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input(prompt_user_chat_)
        with st.sidebar: 
            current_start_time = t.time()
            button = st.button("Send")
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time()
                    cur.execute(f"""
                            SELECT * 
                            FROM chats
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """) 
                    for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                        prompt_history = f"""
                                         \n ------------
                                         \n {name}: {prompt} 
                                         \n Model Output: {output}
                                         \n ------------
                                         \n
                                         """
                    try:
                        response = chat.send_message(prompt_history, **chat_parameters)
                        response = chat.send_message(prompt_user, **chat_parameters)
                        output = response.text 
                    except:
                        output = prompt_error

                    characters = len(prompt_history + prompt_user)
                    input_characters = len(prompt_user)
                    output_characters = len(output)
                    end_time = t.time()
                    SQL = "INSERT INTO chats (name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, prompt_user, output, output, current_model, current_time, current_start_time, end_time, input_characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit()
                    
                    # For Character limit
                    if characters >= character_limit:
                        cur.execute(f"""
                                    UPDATE chats
                                    SET prompt=NULL
                                    """)
                        cur.execute(f"""
                                    UPDATE chats
                                    SET output=NULL
                                    """)
                        con.commit()
                    # st.write(characters)
                        
            st.info(chat_old_info)

            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE chats")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
                
    #-------------------Code (Old Version)---------------------#
    if model == "Code (Old Version)":
        current_model = "Code (Old Version)"
        st.info(info_sample_prompts)
        prompt_user_chat = st.chat_input("What do you want to talk about?")
        with st.sidebar: 
            current_start_time = t.time()
            button = st.button("Send")
            if button or prompt_user_chat:
                if prompt_user_chat:
                    prompt_user = prompt_user_chat
                if prompt_user == "":
                    st.info("Prompt cannot be empty.")
                if (len(prompt_user) >= prompt_character_limit) and GUEST:
                    st.info(f"{prompt_character_limit_text}  \n\n Total Input Characters: {len(prompt_user)}")
                if prompt_user != "" and (len(prompt_user) <= prompt_character_limit or not GUEST):
                    current_start_time = t.time()
                    cur.execute(f"""
                            SELECT * 
                            FROM chats
                            WHERE name='{input_name}'
                            ORDER BY time ASC
                            """)
                    for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                        prompt_history = f"""
                                         \n ------------
                                         \n {name}: {prompt} 
                                         \n Model Output: {output}
                                         \n ------------
                                         \n
                                         """
                    try:
                        response = code_chat.send_message(prompt_history, **code_parameters)
                        response = code_chat.send_message(prompt_user, **code_parameters)
                        output = response.text 
                    except:
                        output = prompt_error

                    characters = len(prompt_history + prompt_user)
                    input_characters = len(prompt_user)
                    output_characters = len(output)
                    end_time = t.time()
                    SQL = "INSERT INTO chats (name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    data = (input_name, prompt_user, prompt_user, output, output, current_model, current_time, current_start_time, end_time, input_characters, output_characters)
                    cur.execute(SQL, data)
                    con.commit()

                    # For Character limit
                    if characters >= character_limit:
                        cur.execute(f"""
                                    UPDATE chats
                                    SET prompt=NULL
                                    """)
                        cur.execute(f"""
                                    UPDATE chats
                                    SET output=NULL
                                    """)
                        con.commit()
                    # st.write(characters)
                        
            st.info(code_old_info)
            
            prune = st.button(":red[Prune History]")
            if prune:
                cur.execute("DROP TABLE chats")
                st.info(prompt_prune_info)
                con.commit()
                st.rerun()
            
    #-------------------Chat Only and Code (Old Version)---------------------#
    if model == "Chat Text Only (Old Version)" or model == "Code (Old Version)":
        cur.execute(f"""
        SELECT * 
        FROM chats
        WHERE name='{input_name}'
        ORDER BY time ASC
        """)
        for id, name, prompt, input_prompt, output, output_history, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
            message = st.chat_message("user")
            message.write(f":blue[{name}]") 
            message.text(f"{input_prompt}")
            message.caption(f"{time} | Input Characters: {total_input_characters}")
            message = st.chat_message("assistant")
            message.markdown(output_history)
            message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}") 
            
        model = "Chat Text Only (Old Version)"
        
    #------------------For Multimodal Guest Limits-----------------------#
    if (guest_limit == True and button) or (guest_limit == True and prompt_user_chat) or (guest_limit == True and button_streaming):
        ### Insert into a database
        SQL = "INSERT INTO multimodal_guest_chats (name, prompt, output, model, time, count_prompt) VALUES(%s, %s, %s, %s, %s, %s);"
        data = (input_name, prompt_user, output, model, current_time, count_prompt)
        cur.execute(SQL, data)
        con.commit()
        
    #----------Prune Admin history and Guest limits using Admin---------#
    if (GUEST == False):
        with st.sidebar:
            prompt_history = st.checkbox("Prompt History")
            if prompt_history:
                # Prune All
                prune_all = st.button(":red[Prune All]")
                
                # Guest Limit
                prune_multimodal_guest_chats = st.button(":red[Prune Guest Limit]")
                if prune_multimodal_guest_chats or prune_all:
                    cur.execute("DROP TABLE multimodal_guest_chats")
                    st.info(f"Guest Limit was successfully deleted.")
                    con.commit()
                
                # All Guest and Admin DB
                prune_db = st.button(":red[Prune Guest and Admin DB]")
                if prune_db or prune_all:
                    admin_DB = ["multimodal", "multimodal_db", "vision_db", "chats_mm", "chats_mm_db", "chats"]
                    for DB in admin_DB:
                        cur.execute(f"DROP TABLE {DB}")
                    con.commit()
                    st.info(f"Admin DB was successfully deleted.")
                    
                # Prune Total Prompts
                prune_total_prompts = st.button(":red[Prune Total Prompts DB]")
                if prune_total_prompts or prune_all:
                    cur.execute("DROP TABLE total_prompts")
                    st.info(f"Total Prompts DB was successfully deleted.")
                    con.commit()
                    
                # Prune Chat View Counter
                prune_chat_view_counter = st.button(":red[Prune Chat View Counter DB]")
                if prune_chat_view_counter or prune_all:
                    cur.execute("DROP TABLE chat_view_counter")
                    st.info(f"Chat View Counter DB was successfully deleted.")
                    con.commit()
                    st.rerun()
                
    #---------------- Insert into a table (total_prompts) ----------------#
    if button or prompt_user_chat:
        SQL = "INSERT INTO total_prompts (name, prompt, output, model, time, count_prompt) VALUES(%s, %s, %s, %s, %s, %s);"
        data = (input_name, prompt_user, output, current_model, current_time, count_prompt)
        cur.execute(SQL, data)
        con.commit()
    
#----------Execution----------#
if __name__ == '__main__':
    # Connection
    con = False
    try:
        con, cur = connection()
        con = True
    except:
        st.info("##### :computer: ```DATABASE CONNECTION: The app can't connect to the database right now. Please try again later.```")
    if con == True:
        # Connection
        con, cur = connection()
        mm_config, mm_chat, multimodal_model, multimodal_generation_config, chat, chat_parameters, code_chat, code_parameters  = models()
        with st.sidebar:
            st.header(":computer: Multimodal Agent ",divider="rainbow")
            # st.caption("## Multimodal Chat Agent")
            st.write(f"Multimodal model can write text, code, analyze images, and more.")
            st.caption("""
                        :warning: :red[Do not add sensitive data.] Your chat will be stored in a database. 
                        
                        """)
            # st.write("Login or Continue as a guest")
            login = st.checkbox("Login")
            guest = st.checkbox("Continue as a guest")
            # Chat View Counter
            time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
            view = 1
            SQL = "INSERT INTO chat_view_counter (view, time) VALUES(%s, %s);"
            data = (view, time)
            cur.execute(SQL, data)
            con.commit()
        if login and guest:
            with st.sidebar:
                st.info("Choose only one")
        elif login:
            with st.sidebar:
                password = st.text_input("Password", type="password")
                agent = st.toggle("**:violet[Start the conversation]**")
            if password == ADMIN_PASSWORD and agent:
                default_name = "Admin"
                GUEST = False
                guest_limit = False
                multimodal(con, cur)
                
                # Counter
                with st.sidebar:
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
                                        FROM chat_view_counter
                                        ORDER BY time DESC
                                        """)
                            for _, _, time in cur.fetchall():
                                st.caption(f"{time}")
                            
            elif password != ADMIN_PASSWORD and agent:
                with st.sidebar:
                    st.info("Wrong Password")

        elif guest:
            default_name = "Guest"
            GUEST = True
            guest_limit = True
            multimodal(con, cur)
        
        elif not login and not guest:
            st.info("Choose login or continue as a guest to get started")
                
        # Close Connection
        cur.close()
        con.close()
        
    #----------Footer----------#
    #----------Sidebar Footer----------#
    with st.sidebar:
        st.markdown("""
                    ---
                    > :gray[:copyright: Portfolio Website by [Matt R.](https://github.com/mregojos)]            
                    > :gray[:cloud: Deployed on [Google Cloud](https://cloud.google.com)]
                    
                    > :gray[For demonstration purposes only to showcase the latest multimodal model capabilities.]
                    ---
                    """)

