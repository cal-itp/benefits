FROM eligibility_verification_client:latest

EXPOSE 5000

WORKDIR /usr/src/server

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py