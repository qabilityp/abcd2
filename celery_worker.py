import email.message
import os
import smtplib
from celery import Celery

import models
from database import db_session, init_db

app = Celery('celery_worker', broker=f"pyamqp://guest@{os.environ.get('RABBIT_HOST', 'localhost')}:5672//")

@app.task
def add(x, y):
    print(x+y)

@app.task
def send_email(contract_id):

    init_db()
    contract = db_session.query(models.Contract).filter_by(id=contract_id).scalar()
    item = db_session.query(models.Item).filter_by(id=contract.item_contract).scalar()

    # creates SMTP session
    #s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    #s.starttls()
    # Authentication
    #s.login("sender_email_id", "sender_email_id_password")
    # message to be sent
    #message = "Message_you_need_to_send"
    msg = email.message.Message()
    msg['Subject'] = 'Test email'
    msg['From'] = 'appemail@exmple.com'
    msg['To'] = 'user1@exmple.com'
    msg.set_payload('Message_you_need_to_send')
    print(msg.as_string())
    # sending the mail
    #s.sendmail("appemail@exmple.com", "user1@exmple.com", message)
    #s.sendmail("appemail@exmple.com", "user2@exmple.com", message)
    # terminating the session
    #s.quit()

