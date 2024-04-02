FROM python:3.11
COPY . /tgbot
WORKDIR /tgbot
RUN pip install -r requirements.txt
EXPOSE 2121
CMD python3 main.py
