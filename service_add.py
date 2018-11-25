from flask import Flask, request, jsonify, make_response
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from database_setup import Base, Service
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta

engine = create_engine('sqlite:///rtds_db.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

service1 = Service(service_name="Photography",
                   service_cat="Product Photography",
                   base_price = 500)
        
service2 = Service(service_name="Photography",
                   service_cat="Layout Photography",
                   base_price = 500)

service3 = Service(service_name="Web Design",
                   service_cat= "Webiste",
                   base_price = 50000)

service4 = Service(service_name="Web Design",
                   service_cat= "Host and Domain",
                   base_price = 12000)

service5 = Service(service_name="Graphic Design",
                   service_cat="Stickers",
                   base_price = 1500)

service6 = Service(service_name="Graphic Design",
                   service_cat="Business Cards",
                   base_price = 1000)

service7 = Service(service_name="Graphic Design",
                   service_cat="Collaterals",
                   base_price = 1500)

service8 = Service(service_name="Graphic Design",
                   service_cat="Layouts",
                   base_price = 1200)

service9 = Service(service_name="Branding",
                   service_cat="Logo Design",
                   base_price = 5000)

service10 = Service(service_name="Branding",
                   service_cat="Premium Logo Design",
                   base_price = 10000)

service11 = Service(service_name="Digital Marketing",
                   service_cat="Monthly",
                   base_price = 10000)


session.add(service1)
session.add(service2)
session.add(service3)
session.add(service4)
session.add(service5)
session.add(service6)
session.add(service7)
session.add(service8)
session.add(service9)
session.add(service10)
session.add(service11)
session.commit()
