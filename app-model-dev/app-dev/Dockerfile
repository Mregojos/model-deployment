FROM python
COPY requirements.txt .
RUN pip install -U -r requirements.txt -q
WORKDIR /app
COPY . /app
# ENV DBNAME="" USER="" HOST="" DBPORT="" DBPASSWORD="" PROJECT_NAME="" 
EXPOSE 9000
CMD ["streamlit", "run", "app-model-ii-edited.py", "--server.address", "0.0.0.0", "--server.port", "9000"]
