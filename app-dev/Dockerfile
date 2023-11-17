FROM python
WORKDIR /app
RUN pip install streamlit psycopg2-binary google-cloud-aiplatform -q
COPY . /app
EXPOSE 9000
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "9000"]
