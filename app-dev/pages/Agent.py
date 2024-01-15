#----------Import libraries----------# 
import streamlit as st
import psycopg2
import os
import time as t
import vertexai
from vertexai.language_models import TextGenerationModel, CodeGenerationModel
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
    cur.execute("CREATE TABLE IF NOT EXISTS multimodal(name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, image_detail varchar, saved_image_data_base_string varchar, total_input_characters int, total_output_characters int)")
    
    # Vision
    # cur.execute("DROP TABLE vision_db")
    cur.execute("CREATE TABLE IF NOT EXISTS vision_db(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, saved_image_data_base_string varchar)")

    # Chat Text Only
    # cur.execute("DROP TABLE chats_mm")
    cur.execute("CREATE TABLE IF NOT EXISTS chats_mm(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")
    # cur.execute("DROP TABLE chats")
    cur.execute("CREATE TABLE IF NOT EXISTS chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")

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
    text_model = TextGenerationModel.from_pretrained("text-bison")

    #----------Vertex AI Code----------#
    code_model = CodeGenerationModel.from_pretrained("code-bison")
    

    return mm_model, mm_config, mm_chat, multimodal_model, multimodal_generation_config, text_model, code_model


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
    sleep_time = 1
    limit_query = 1
    id_num = 1
    id_add = 1
    
    #------------------ Admin --------------------------#
    with st.sidebar:
        if GUEST == False:
            input_name = st.text_input("Name", default_name)
            #------------------- Saved Conversations -------------------#
            # topic_name = st.text_input("Create a topic or use saved conversation")
            # saved_conversations = st.checkbox("Saved Conversations")
            # if saved_conversations:
            #     conversations = st.selectbox("Saved Convesations", [])
            # if topic_name == "":
            #     st.info("Please choose a topic or use saved conversation")

    #------------------ Guest Counter ------------------#
    with st.sidebar:
        # guest_time = t.strftime("%Y-%m-%d-%H")
        if GUEST == True:
            input_name = st.text_input("Username")
            start_guest = st.button("Start the conversation")
            if input_name == "" and start_guest:
                st.info("Please input your username first")
            # input_name = st.text_input("Name", f"{default_name}")
            # input_name = st.text_input("Name", f"{default_name}-{guest_time}")
            if input_name == "Admin":
                input_name = ""
                st.info("Please use different username.")
    LIMIT = 30
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
                You can now start the conversation by prompting in the text bar. :smile: You can ask:
                * List the things you are capable of doing 
                * What is Cloud Computing? Explain it at different levels, such as beginner, intermediate, and advanced
                * What is Google Cloud? Important Google Cloud Services to know
                * Compare Site Reliability Engineering with DevOps
                * Tell me about different cloud services
                * Explain Multimodal Model in simple terms
                """
    vision_info_ = """
                You can now upload an image to analyze.
                """
    
    with st.sidebar:


        #------------------ prompt_info ------------------#
        prompt_history = ""
        
        vision_info = f":violet[{model}] analyzes the photo you uploaded."
        vision_db_info = f":violet[{model}] analyzes the photo you uploaded and saves to the database. This model does not have chat capability."
        chat_latest_old_info = f":violet[{model}] compares the latest model to the old model."
        
        prompt_prune_info = f"{input_name}'s prompts and output data have successfully been deleted."
        prompt_error = "Sorry about that. Please prompt it again, prune the history, or change the model if the issue persists."
        prompt_user_chat_ = "What do you want to talk about?"

    #------------------ Guest limit --------------------------#
    if GUEST == True and total_count >= LIMIT:
        with st.sidebar:
            st.info("Guest daily limit has been reached.")

            # If the limit is reached, this will automatically delete all Guest prompt history. Note: "multimodal_guest_chats" is not included.
            guest_DB = ["multimodal", "vision_db", "chats_mm", "chats"]
            for DB in guest_DB:
                cur.execute(f"DROP TABLE {DB}")
            con.commit()
            
        st.info("Guest daily limit has been reached.")

    #-------------------Conversation starts here---------------------#
    #-------------------Multimodal (Multi-Turn)---------------------#
    if input_name != "" :
        with st.sidebar:
            #------------------ Prompt starts --------------------------#
            if (GUEST == False) or (GUEST == True and total_count < LIMIT): 
                model = st.selectbox("Choose Model", (["Multimodal (Multi-Turn)", "Multimodal (One-Turn)", "Vision (One-Turn)", "Vision (One-Turn) with DB", "Latest vs Old Model / Multi-Turn / Text Only", "Text Only (One-Turn)", "Text Only (Multi-Turn)", "Text Only (Old Version / Multi-Turn)", "Code (Old Version / Multi-Turn)" ]))
                prompt_user = st.text_area("Prompt")                
                uploaded_file = None
                current_image_detail = ""
                image_data_base_string = ""
                current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
            
        if model == "Multimodal (Multi-Turn)":
            current_model = "Multimodal (Multi-Turn)"
            st.info(info_sample_prompts)
            prompt_user_chat = st.chat_input(prompt_user_chat_)
            prompt_history = ""
            with st.sidebar:
                image = st.checkbox("Add a photo")
                add_data = st.checkbox("Add additional context")
                if add_data:
                    prompt_history = st.text_area("Additional Context")
                    prompt_history = "Additional information: " + "\n\n" + prompt_history + "\n\n"
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
                        # responses = multimodal_model.generate_content(["Explain the image in detail", image], generation_config=multimodal_generation_config)
                        # current_image_detail = responses.text
                    else:
                        image_data_base_string = ""

                current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
                button = st.button("Generate")
                if button or prompt_user_chat:
                    if prompt_user_chat:
                        prompt_user = prompt_user_chat
                    if prompt_user == "":
                        st.info("Prompt cannot be empty.")
                    if (len(prompt_user + prompt_history) >= prompt_character_limit) and GUEST:
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
                            with st.spinner("Generating..."):
                                for name, prompt, output, model, time, start_time, end_time, image_detail, saved_image_data_base_string, total_input_characters, total_output_characters in cur.fetchall():
                                    prompt_history = prompt_history + f"\n\n Prompt ID: {id_num}" +  f"\n\n User: {prompt}" + f"\n\n Model: {output}"
                                    id_num += id_add

                                if prompt_history == "":
                                    if uploaded_file is not None:
                                        responses = multimodal_model.generate_content([prompt_user, image], generation_config=multimodal_generation_config)
                                        current_image_detail = responses.text
                                        output = responses.text
                                    if uploaded_file is None:
                                        response = mm_model.generate_content(prompt_user)
                                        output = response.text
                                if prompt_history != "":
                                    if uploaded_file is not None:
                                        responses = multimodal_model.generate_content([prompt_user, image], generation_config=multimodal_generation_config)
                                        current_image_detail = responses.text
                                        # prompt_history = prompt_history + f"\n\n Prompt ID: Latest" + f"\n\n User: {prompt_user}" 
                                        # response = mm_model.generate_content(f"{prompt_history}. Image information: {current_image_detail}")
                                        # prompt_history = prompt_history + f"\n\n Prompt ID: Latest" + f"\n\n User: {prompt_user}" 
                                        response = multimodal_model.generate_content([prompt_user, image], generation_config=multimodal_generation_config)
                                        output = response.text
                                    if uploaded_file is None:
                                        prompt_history = prompt_history + f"\n\n Prompt ID: Latest" + f"\n\n User: {prompt_user}" 
                                        response = mm_model.generate_content(prompt_history)
                                        output = response.text
                            # st.write(prompt_history)
                        except: 
                            output = prompt_error
                        # except Exception as e:
                        #    if not GUEST:
                        #        st.write(e)

                        input_characters = len(prompt_user)
                        output_characters = len(output)
                        end_time = t.time() 
                        SQL = "INSERT INTO multimodal (name, prompt, output, model, time, start_time, end_time, saved_image_data_base_string, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                        data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, image_data_base_string, input_characters, output_characters)
                        cur.execute(SQL, data)
                        con.commit()

                refresh = st.button(":blue[Reset]")
                if refresh:
                    st.rerun()

                prune = st.button(":red[Prune History]")
                if prune:
                    cur.execute(f"""
                                DELETE  
                                FROM multimodal
                                WHERE name='{input_name}'
                                """)
                    # cur.execute("DROP TABLE multimodal")
                    # cur.execute("CREATE TABLE IF NOT EXISTS multimodal(name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, image_detail varchar, saved_image_data_base_string varchar, total_input_characters int, total_output_characters int)")
                    con.commit()
                    st.info(prompt_prune_info)
                    t.sleep(sleep_time)
                    st.rerun()

            cur.execute(f"""
            SELECT * 
            FROM multimodal
            WHERE name='{input_name}'
            ORDER BY time ASC
            """)
            for name, prompt, output, model, time, start_time, end_time, image_detail, saved_image_data_base_string, total_input_characters, total_output_characters in cur.fetchall():
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
                            with st.spinner("Generating..."):
                                if uploaded_file is not None:
                                    response = mm_model.generate_content(f"{prompt_user}. I add an image: {current_image_detail}")
                                    output = response.text
                                if uploaded_file is None:
                                    response = mm_model.generate_content(prompt_user)
                                    output = response.text
                        except:
                            output = prompt_error
                        input_characters = len(prompt_user)
                        output_characters = len(output)
                        end_time = t.time() 

                response = ""
                response_ = ""
                button_streaming = st.button("Generate (Streaming)")
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
                                response = mm_model.generate_content(f"{prompt_user}. I add an image: {current_image_detail}"  , stream=True)
                            if uploaded_file is None:
                                response = mm_model.generate_content(prompt_user, stream=True)
                        except:
                            output = prompt_error

                    input_characters = len(prompt_user)

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
                try:
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

                except:
                    st.info(prompt_error)
                    # st.rerun()

            model = "Multimodal (One-Turn)"

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
                    button = st.button("Generate")
                    with st.spinner("Generating..."):
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

                refresh = st.button(":blue[Reset]")
                if refresh:
                    st.rerun()

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
                button = st.button("Generate")
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
                            with st.spinner("Generating..."):
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

                refresh = st.button(":blue[Reset]")
                if refresh:
                    st.rerun()

                prune = st.button(":red[Prune History]")
                if prune:
                    cur.execute("DROP TABLE vision_db")
                    cur.execute("CREATE TABLE IF NOT EXISTS vision_db(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, saved_image_data_base_string varchar)")              
                    con.commit()
                    st.info(prompt_prune_info)
                    t.sleep(sleep_time)
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

        #-------------------Comparison: Chat Text Only (Latest vs Old Version)---------------------------------------#
        if model == "Latest vs Old Model / Multi-Turn / Text Only":
            st.info(info_sample_prompts)
            prompt_user_chat = st.chat_input(prompt_user_chat_)
            prompt_history = ""
            old_prompt_history = ""
            with st.sidebar:
                button = st.button("Generate")
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
                            with st.spinner("Generating..."):
                                for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                                    prompt_history = prompt_history + f"\n\n Prompt ID: {id}" +  f"\n\n User: {prompt}" + f"\n\n Model: {output}"

                                if prompt_history == "":
                                    response = mm_model.generate_content(prompt_user)                         
                                if prompt_history != "":
                                    prompt_history = prompt_history + f"\n\n Prompt ID: Latest" + f"\n\n User: {prompt_user}" 
                                    response = mm_model.generate_content(prompt_history)
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

                        #-------------------Chat Text Only Old Version---------------------#
                        current_start_time = t.time()
                        current_model = "Old Version"
                        cur.execute(f"""
                                SELECT * 
                                FROM chats
                                WHERE name='{input_name}'
                                ORDER BY time ASC
                                """) 
                        try:
                            with st.spinner("Generating..."):
                                for id, name, old_prompt, old_output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                                    old_prompt_history = old_prompt_history + f"\n\n Prompt ID: {id}" +  f"\n\n User: {old_prompt}" + f"\n\n Model: {old_output}"

                                if old_prompt_history == "":
                                    response = code_model.predict(prompt_user)                         
                                if old_prompt_history != "":
                                    old_prompt_history = old_prompt_history + f"\n\n Prompt ID: Latest" + f"\n\n User: {prompt_user}" 
                                    response = code_model.predict(old_prompt_history)
                                output = response.text 
                        except:
                            output = prompt_error

                        characters = len(old_prompt_history + prompt_user)
                        input_characters = len(prompt_user)
                        output_characters = len(output)
                        end_time = t.time()
                        SQL = "INSERT INTO chats (name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                        data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, input_characters, output_characters)
                        cur.execute(SQL, data)
                        con.commit()

                st.info(chat_latest_old_info)

                refresh = st.button(":blue[Reset]")
                if refresh:
                    st.rerun()

                prune = st.button(":red[Prune History]")
                if prune:
                    cur.execute("DROP TABLE chats_mm")
                    cur.execute("CREATE TABLE IF NOT EXISTS chats_mm(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")
                    cur.execute("DROP TABLE chats")
                    cur.execute("CREATE TABLE IF NOT EXISTS chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")
                    con.commit()
                    st.info(prompt_prune_info)
                    t.sleep(sleep_time)
                    st.rerun()

            col_A, col_B = st.columns(number_columns)

            with col_A:
                #-------------------Chat Text Only Latest Version---------------------#
                st.info("Latest Model") 
                with st.expander("Latest Version Past Conversations"):
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

                cur.execute(f"""
                SELECT * 
                FROM chats_mm
                WHERE name='{input_name}'
                ORDER BY time DESC
                LIMIT {limit_query}
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
                st.info("Old Model") 
                with st.expander("Old Version Past Conversations"):
                    cur.execute(f"""
                    SELECT * 
                    FROM chats
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
                    model = "Old Version"

                cur.execute(f"""
                SELECT * 
                FROM chats
                WHERE name='{input_name}'
                ORDER BY time DESC
                LIMIT {limit_query}
                """)
                for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                    message = st.chat_message("user")
                    message.write(f":blue[{name}]") 
                    message.text(f"{prompt}")
                    message.caption(f"{time} | Input Characters: {total_input_characters}")
                    message = st.chat_message("assistant")
                    message.markdown(output)
                    message.caption(f"{time} | Model: {model} | Processing Time: {round(end_time-start_time, round_number)} seconds | Output Characters: {total_output_characters}") 
                model = "Old Version"

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
                            with st.spinner("Generating..."):
                                response = mm_model.generate_content(prompt_user, generation_config=mm_config)
                                output = response.text
                        except:
                            output = prompt_error
                        input_characters = len(prompt_user)
                        output_characters = len(output)
                        end_time = t.time() 

                response_ = ""
                button_streaming = st.button("Generate (Streaming)")
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
                            response = mm_model.generate_content(prompt_user, stream=True, generation_config=mm_config)
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
                try: 
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
                except:
                    st.info(prompt_error)

            model = "Text Only (One-Turn)"

        #-------------------Text Only (Multi-Turn)---------------------#
        if model == "Text Only (Multi-Turn)":
            current_model = "Text Only (Multi-Turn)"
            st.info(info_sample_prompts)
            prompt_user_chat = st.chat_input(prompt_user_chat_)
            prompt_history = ""
            with st.sidebar:
                current_time = t.strftime("Date: %Y-%m-%d | Time: %H:%M:%S UTC")
                button = st.button("Generate")
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
                            with st.spinner("Generating..."):
                                for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                                    prompt_history = prompt_history + f"\n\n Prompt ID: {id}" +  f"\n\n User: {prompt}" + f"\n\n Model: {output}"

                                if prompt_history == "":
                                    response = mm_model.generate_content(prompt_user)                         
                                if prompt_history != "":
                                    prompt_history = prompt_history + f"\n\n Prompt ID: Latest" + f"\n\n User: {prompt_user}" 
                                    response = mm_model.generate_content(prompt_history)
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

                refresh = st.button(":blue[Reset]")
                if refresh:
                    st.rerun()

                prune = st.button(":red[Prune History]")
                if prune:
                    cur.execute("DROP TABLE chats_mm")
                    cur.execute("CREATE TABLE IF NOT EXISTS chats_mm(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")
                    con.commit()
                    st.info(prompt_prune_info)
                    t.sleep(sleep_time)
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

            model = "Text Only (Multi-Turn)"



        #-------------------Old Version---------------------------------#
        #-------------------Text Only (Old Version)---------------------#
        if model == "Text Only (Old Version / Multi-Turn)":
            current_model = "Text Only (Old Version / Multi-Turn)"
            st.info(info_sample_prompts)
            prompt_user_chat = st.chat_input(prompt_user_chat_)
            prompt_history = ""
            with st.sidebar: 
                current_start_time = t.time()
                button = st.button("Generate")
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
                        try:
                            with st.spinner("Generating..."):
                                for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                                    prompt_history = prompt_history + f"\n\n Prompt ID: {id}" +  f"\n\n User: {prompt}" + f"\n\n Model: {output}"

                                if prompt_history == "":
                                    response = text_model.predict(prompt_user)                         
                                if prompt_history != "":
                                    prompt_history = prompt_history + f"\n\n Prompt ID: Latest" + f"\n\n User: {prompt_user}" 
                                    response = text_model.predict(prompt_history)
                                output = response.text   
                        except:
                            output = prompt_error

                        characters = len(prompt_history + prompt_user)
                        input_characters = len(prompt_user)
                        output_characters = len(output)
                        end_time = t.time()
                        SQL = "INSERT INTO chats (name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                        data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, input_characters, output_characters)
                        cur.execute(SQL, data)
                        con.commit()

                refresh = st.button(":blue[Reset]")
                if refresh:
                    st.rerun()

                prune = st.button(":red[Prune History]")
                if prune:
                    cur.execute("DROP TABLE chats")
                    cur.execute("CREATE TABLE IF NOT EXISTS chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")
                    con.commit()
                    st.info(prompt_prune_info)
                    t.sleep(sleep_time)
                    st.rerun()

            model = "Text Only (Old Version / Multi-Turn)"

        #-------------------Code (Old Version)---------------------#
        if model == "Code (Old Version / Multi-Turn)":
            current_model = "Code Only (Old Version / Multi-Turn)"
            st.info(info_sample_prompts)
            prompt_user_chat = st.chat_input(prompt_user_chat_)
            prompt_history = ""
            with st.sidebar: 
                current_start_time = t.time()
                button = st.button("Generate")
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
                        try:
                            with st.spinner("Generating..."):
                                for id, name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters in cur.fetchall():
                                    prompt_history = prompt_history + f"\n\n Prompt ID: {id}" +  f"\n\n User: {prompt}" + f"\n\n Model: {output}"

                                if prompt_history == "":
                                    response = code_model.predict(prompt_user)                         
                                if prompt_history != "":
                                    prompt_history = prompt_history + f"\n\n Prompt ID: Latest" + f"\n\n User: {prompt_user}" 
                                    response = code_model.predict(prompt_history)
                                output = response.text   
                        except:
                            output = prompt_error

                        characters = len(prompt_history + prompt_user)
                        input_characters = len(prompt_user)
                        output_characters = len(output)
                        end_time = t.time()
                        SQL = "INSERT INTO chats (name, prompt, output, model, time, start_time, end_time, total_input_characters, total_output_characters) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                        data = (input_name, prompt_user, output, current_model, current_time, current_start_time, end_time, input_characters, output_characters)
                        cur.execute(SQL, data)
                        con.commit()

                refresh = st.button(":blue[Reset]")
                if refresh:
                    st.rerun()

                prune = st.button(":red[Prune History]")
                if prune:
                    cur.execute("DROP TABLE chats")
                    cur.execute("CREATE TABLE IF NOT EXISTS chats(id serial PRIMARY KEY, name varchar, prompt varchar, output varchar, model varchar, time varchar, start_time float, end_time float, total_input_characters int, total_output_characters int)")
                    con.commit()
                    st.info(prompt_prune_info)
                    t.sleep(sleep_time)
                    st.rerun()

            model = "Code (Old Version / Multi-Turn)"

        #-------------------Text and Code (Old Version)---------------------#
        if model == "Text Only (Old Version / Multi-Turn)" or model == "Code (Old Version / Multi-Turn)":
            cur.execute(f"""
            SELECT * 
            FROM chats
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

            model = "Chat Text Only (Old Version)"

        #------------------For Multimodal Guest Limits-----------------------#
        if (guest_limit == True and button) or (guest_limit == True and prompt_user_chat) or (guest_limit == True and button_streaming):
            ### Insert into a database
            SQL = "INSERT INTO multimodal_guest_chats (name, prompt, output, model, time, count_prompt) VALUES(%s, %s, %s, %s, %s, %s);"
            data = (input_name, prompt_user, output, model, current_time, count_prompt)
            cur.execute(SQL, data)
            con.commit()

        if GUEST == True:
            with st.sidebar:
                guest_counter = st.checkbox("Guest Limit")
                if guest_counter:
                    st.write(f"""
                            * Guest Daily Limit Left: {LIMIT - total_count}
                            """)

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
                        admin_DB = ["multimodal", "vision_db", "chats_mm", "chats"]
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
        if button or prompt_user_chat or button_streaming:
            SQL = "INSERT INTO total_prompts (name, prompt, output, model, time, count_prompt) VALUES(%s, %s, %s, %s, %s, %s);"
            data = (input_name, prompt_user, output, current_model, current_time, count_prompt)
            cur.execute(SQL, data)
            con.commit()

        #----------------- About the mnodel -------------------------------#
        with st.sidebar:
            about_models = st.checkbox("Model Details")
            if about_models:
                st.write("""
                        * Latest models use Gemini Pro and Gemini Pro Vision. Older models use PaLM Text and Code.
                        """)
                
        #---------------- Counter ---------------------------------------#
        with st.sidebar:
            if GUEST == False:
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
        mm_model, mm_config, mm_chat, multimodal_model, multimodal_generation_config, text_model, code_model  = models()
        with st.sidebar:
            st.header(":brain: Multimodal Agent :computer: ",divider="rainbow")
            # st.caption("## Multimodal Chat Agent")
            st.write(f"Multimodal model can generate text, code, analyze images, and more.")
            st.write("""
                        ###### :warning: :red[Do not add sensitive data.] Your chat will be stored in a database.
                        
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
                    
                    > :gray[For demonstration purposes only,     
                    > to showcase the latest multimodal model capabilities.]
                    ---
                    """)


