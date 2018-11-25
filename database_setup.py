import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean, Float, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Admin(Base):
    __tablename__= 'admin'

    admin_id = Column(Integer, primary_key=True)
    public_id = Column(String(50), unique=True)
    admin_firstname = Column(String(20))
    admin_lastname = Column(String(20))
    admin_email =  Column(String(30))
    last_update = Column(DateTime)
    date_created = Column(DateTime)
    password = Column(String(30))
    admin = Column(Boolean)

class Client(Base):
    __tablename__= 'client'

    client_id = Column(Integer, primary_key=True)
    client_firstname = Column(String(20))
    client_lastname = Column(String(20))
    client_email =  Column(String(30))
    client_landline = Column(Integer)
    company_name = Column(String(50))
    client_mobile = Column(Integer)
    client_fax = Column(Integer)
    client_address = Column(String(40))
    date_created = Column(DateTime)
    date_updated = Column(DateTime)
    public_id = Column(String(50), unique=True)
    password = Column(String(30))
    admin = Column(Boolean)

class Service(Base):
    __tablename__= 'service'

    service_id = Column(Integer, primary_key=True)
    service_name = Column(String(20), nullable=False)
    service_cat = Column(String(20), nullable=False)
    base_price = Column(Float, nullable=False)

class Quotation(Base):
    __tablename__ = 'quotation'

    quote_id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.client_id'))
    quote_validity = Column(DateTime)
    date_created = Column(DateTime)
    is_package = Column(Boolean)
    quote_status = Column(String(8))
    package_id = Column(String(11))
    last_updated = Column(DateTime)
    generated_id = Column(String(50), unique=True)
    promo = Column(String(10))
    
    client = relationship(Client)

class QuotationDetail(Base):
    __tablename__ = 'quotation_detail'

    quote_detail_id = Column(Integer, primary_key=True)
    desc = Column(String(100))
    qty = Column(Integer)
    unit_price = Column(Float)
    service_id =  Column(Integer, ForeignKey('service.service_id'))
    quote_id = Column(Integer, ForeignKey('quotation.quote_id'))

    service = relationship(Service)
    quotation = relationship(Quotation)

# class Project(Base):
#     __tablename__= 'project'

#     project_id = Column(Integer, primary_key=True)
#     date_created = Column(DateTime)
#     client_id = Column(Integer, ForeignKey('client.client_id'))
#     project_title = Column(String(20))
#     quote_id = Column(Integer, ForeignKey('quotation.quote_id'))
#     generated_id = Column(String(50), unique=True)
    
#     client = relationship(Client)
#     quotation = relationship(Quotation)

# class ProjectDetail(Base):
#     __tablename__ ='project_detail'

#     project_detail_id = Column(Integer, primary_key=True)
#     project_cat = Column(String(20), nullable=False)
#     project_desc  = Column(String(20), nullable=False)
#     project_status  = Column(String(8), nullable=False)
#     last_update = Column(DateTime, nullable=False)
#     admin_id = Column(Integer, ForeignKey('admin.admin_id'))
#     project_id = Column(Integer, ForeignKey('project.project_id'))

#     admin = relationship(Admin)
#     project = relationship(Project)

# class Package(Base):
#     __tablename__ = "package"

#     package_id = Column(Integer, primary_key=True)
#     service_id = Column(Integer, ForeignKey('service.service_id'))
#     date_created = Column(DateTime, nullable=False)
#     service = relationship(Service)

# class PackageDetail(Base):
#     __tablename__ = "package_detail"

#     package_detail_id = Column(Integer, primary_key = True)
#     package_name = Column(String(20), nullable=False)
#     price = Column(Float, nullable=False)
#     package_type = Column(String(10), nullable=False)
#     last_updated = Column(DateTime, nullable=False)
#     package_id = Column(Integer, ForeignKey('package.package_id'))

#     package = relationship(Package)

class Invoice(Base):
    __tablename__="invoice"

    invoice_id = Column(Integer, primary_key=True)
    invoice_no = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    quote_id = Column(Integer, ForeignKey('quotation.quote_id'))
    paid = Column(String(10))
    
    quotation = relationship(Quotation)

class Promo(Base):
    __tablename__="promo"

    promo_id = Column(Integer, primary_key=True)
    promo_name = Column(String(10))
    off = Column(Float)
    priveledge_to = Column(Integer, ForeignKey('client.client_id'))

    client = relationship(Client)
       
engine = create_engine('sqlite:///rtds_db.db')
Base.metadata.create_all(engine)
