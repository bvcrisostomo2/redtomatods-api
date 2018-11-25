from flask import Flask, request, jsonify, make_response
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from database_setup import Base, Admin, Client
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta

engine = create_engine('sqlite:///rtds_db.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

hashed_password = generate_password_hash("123456", method='sha256')
new_admin = Admin(public_id=str(uuid.uuid4()),
                     admin_firstname="Ragine",
                     admin_lastname="Tumulak",
                     admin_email="ragine_tumulak@gmail.com",
                     date_created=datetime.datetime.now(),
                     last_update=datetime.datetime.now(),
                     password=hashed_password, 
                     admin=True)
session.add(new_admin)

hashed_password = generate_password_hash('OMG123', method='sha256')

new_client = Client(public_id=str(uuid.uuid4()),  
                    client_firstname="Zhellah",
                    client_lastname="Punzalan",
                    client_email= "omg@gmail.com",
                    company_name = "Oil My Goodness",
                    client_landline="None",
                    client_mobile="None",
                    client_fax="None",
                    client_address="Caloocan",
                    date_created=datetime.datetime.now(),
                    date_updated=datetime.datetime.now(),
                    password=hashed_password, 
                    admin=False)
session.add(new_client)

hashed_password2 = generate_password_hash('OMG123', method='sha256')

new_client2 = Client(public_id=str(uuid.uuid4()),  
                    client_firstname="Zhellah",
                    client_lastname="Punzalan",
                    client_email= "zeephora@gmail.com",
                    company_name = "Zeephora",
                    client_landline="None",
                    client_mobile="None",
                    client_fax="None",
                    client_address="Caloocan",
                    date_created=datetime.datetime.now(),
                    date_updated=datetime.datetime.now(),
                    password=hashed_password, 
                    admin=False)
session.add(new_client2)

session.commit()
