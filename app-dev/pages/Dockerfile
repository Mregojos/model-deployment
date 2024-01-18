FROM python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -q
# RUN pip install -U -r requirements.txt -q
COPY . /app
EXPOSE 9000
CMD ["streamlit", "run", "Agent.py", "--server.address", "0.0.0.0", "--server.port", "9000", "--client.toolbarMode", "minimal", "--global.disableWidgetStateDuplicationWarning", "true"]
