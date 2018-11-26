from flask import Flask, request, jsonify, make_response, Response
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from database_setup import Base, Admin, Client, Quotation, QuotationDetail, Service, Invoice, Promo
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
import operator 

app = Flask(__name__)

app.config['SECRET_KEY'] = 'rtds-secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'rtds_db.db'

engine = create_engine('sqlite:///rtds_db.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

######################################TOKEN######################################################################
def token_required_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = session.query(Admin).filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def token_required_client(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = session.query(Client).filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
######################################ADMIN######################################################################
@app.route('/api/dashboard', methods=['GET'])
def view_dashboard():
    invoices = session.query(Invoice).filter_by(paid="Paid").all()

    output_data = {}
    output_data['total_sales'] = 0
    output_data['most_availed_service'] = ""
    output_data['most_reccuring_costumer'] = ""
    output_data['net_sales'] = 0
    output_data['less_tax'] = 0

    service_counts = {}
    client_counts = {}

    for invoice in invoices:
        quotation = session.query(Quotation).filter_by(quote_id=invoice.quote_id).first()
        quotation_details = session.query(QuotationDetail).filter_by(quote_id=quotation.quote_id).all()
        for quotation_detail in quotation_details:
            quotation_detail_total = quotation_detail.unit_price * quotation_detail.qty
            output_data['total_sales'] += quotation_detail_total
            if quotation_detail.service_id in service_counts:
                service_counts[quotation_detail.service_id] += 1
            else:
                service_counts[quotation_detail.service_id] = 1

        if quotation.client_id in client_counts:
            client_counts[quotation.client_id] += 1
        else:
            client_counts[quotation.client_id] = 1

    if service_counts:
        service_max = session.query(Service).filter_by(service_id=max(service_counts, key=service_counts.get)).one()
        output_data['most_availed_service'] = service_max.service_name + " " + service_max.service_cat
    
    if client_counts:
        client_max = session.query(Client).filter_by(client_id=max(client_counts, key=client_counts.get)).one()
        output_data['most_reccuring_costumer'] = client_max.company_name

    
    expenses = 10000
    output_data['net_sales'] = output_data['total_sales'] - expenses
    output_data['less_tax'] = output_data['net_sales'] - (output_data['net_sales']*.20)

    return  jsonify(output_data)

#GET ALL
#@token_required_admin
@app.route('/api/clients/', methods=['GET'])
#def get_all_clients(current_user):
def get_all_clients():
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    clients = session.query(Client).all()
    
    output = []
    for client in clients:
        client_data = {}
        client_data['client_id'] = client.client_id
        client_data['client_firstname'] = client.client_firstname
        client_data['client_lastname'] = client.client_lastname
        client_data['client_landline'] = client.client_landline
        client_data['company_name'] = client.company_name
        client_data['client_mobile'] = client.client_mobile
        client_data['client_fax'] = client.client_fax
        client_data['client_email'] = client.client_email
        client_data['client_address'] = client.client_address
        client_data['date_created'] = client.date_created
        client_data['date_updated'] = client.date_updated
        client_data['public_id'] = client.public_id
        client_data['admin'] = client.admin
        output.append(client_data)
    return jsonify({'clients' : output})

@app.route('/api/clients/<public_id>', methods=['GET'])
# @token_required_admin
#def view_client(current_user, public_id):
def view_client(public_id):

    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    client = session.query(Client).filter_by(public_id=public_id).one()
    quotations = session.query(Quotation).filter_by(client_id=client.client_id).all()

    output_data = {}
    client_list = []
    client_data = {}
    client_data['company_name'] = client.company_name
    client_list.append(client_data)

    quotation_list = []
    invoice_list = []

    for quotation in quotations:
        quotation_data = {} 
        quotation_data['quote_id'] = quotation.quote_id
        quotation_data['client_id'] = quotation.client_id
        quotation_data['quote_validity'] = quotation.quote_validity
        quotation_data['data_created'] = quotation.date_created
        quotation_data['is_package'] = quotation.is_package
        quotation_data['package_id'] = quotation.package_id
        quotation_data['last_updated'] = quotation.last_updated
        quotation_data['generated_id'] = quotation.generated_id
        quotation_data['quote_status'] = quotation.quote_status
        quotation_list.append(quotation_data)

        invoices = session.query(Invoice).filter_by(quote_id=quotation.quote_id).all()
        for invoice in invoices:
            quotation_details = session.query(QuotationDetail).filter_by(quote_id=invoice.quote_id).all()
            total = 0
            for quotation_detail in quotation_details:
                total += quotation_detail.unit_price * quotation_detail.qty
            invoice_data = {}            
            invoice_data['invoice_id'] = invoice.invoice_id
            invoice_data['invoice_no'] = invoice.invoice_no
            # invoice_data['date_created'] = invoice.date_created
            invoice_data['quote_id'] = invoice.quote_id
            invoice_data['total price'] = total
            invoice_data['paid'] = invoice.paid
            invoice_list.append(invoice_data)


    output_data['client'] = client_list
    output_data['quotations'] = quotation_list
    output_data['invoices'] = invoice_list

    return jsonify(output_data)

@app.route('/api/quotation/<quote_id>', methods=['GET'])
#@token_required_admin
# def view_quotation(current_user, quote_id):
def get_quotation(quote_id):    
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    quotation = session.query(Quotation).filter_by(quote_id=quote_id).first()

    if not quotation:
        return jsonify({'message': "no quotation"})

    client = session.query(Client).filter_by(client_id=quotation.client_id).first()
    
    output_data = {}
    total = 0
    
    output_data['quote_id'] = quotation.quote_id
    output_data['quote_validity'] = quotation.quote_validity
    output_data['date_created'] = quotation.date_created
    output_data['is_package'] = quotation.is_package
    output_data['quote_status'] = quotation.quote_status
    output_data['package_id'] = quotation.package_id
    output_data['last_updated'] = quotation.last_updated
    output_data['generated_id'] = quotation.generated_id
      
    quotation_details = session.query(QuotationDetail).filter_by(quote_id=quotation.quote_id).all()
      
    output_data['quotation_details'] = []
    for quotation_detail in quotation_details:
        quotation_details_data = {}
        quotation_details_data['desc'] = quotation_detail.desc
        quotation_details_data['qty'] = quotation_detail.qty
        quotation_details_data['unit_price'] = quotation_detail.unit_price
        quotation_details_data['service_id'] = quotation_detail.service_id
        quotation_details_data['quote_id'] = quotation_detail.quote_id
        output_data['quotation_details'].append(quotation_details_data)
        total += (quotation_detail.unit_price * quotation_detail.qty)

    invoice = session.query(Invoice).filter_by(quote_id=quote_id).first()
    if invoice:
        invoice_data={}
        invoice_data['invoice_no'] = invoice.invoice_no
        invoice_data['invoice_id'] = invoice.invoice_id
        invoice_data['status'] = invoice.paid
        invoice_data['date_created'] = invoice.date_created
        
    else:
        invoice_data={}
        invoice_data['invoice_no'] = ""
        invoice_data['invoice_id'] = ""
        invoice_data['status'] = ""
        invoice_data['date_created'] = ""

    output_data['invoice'] = invoice_data
    output_data['total_sales'] = total
    output_data['company_name'] = client.company_name
        
    return jsonify(output_data)

@app.route('/api/quotation/<quote_id>', methods=['PUT'])
# @token_required_admin
# def update_quotation_status(current_user, quote_id):
def update_quote_status(quote_id):
    
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    quote = session.query(Quotation).filter_by(quote_id=quote_id).first()
    
    if not quote:
        return jsonify({'message' : 'No quote found!'})

    if quote.quote_status == "Approved by Admin":
        return jsonify({'message':"Already approved by admin"})

    if quote.quote_status == "Approved by Both":
        return jsonify({'message':"Already approved by both"})

    if quote.quote_status == "For Approval":
        quote.quote_status = "Approved by Admin"
        quote.quote_validity = datetime.datetime.now() + timedelta(days=7)
        session.commit()
    

    return jsonify({'message' : 'The quotation has been updated!'})

@app.route('/api/quotation/<quote_id>/reject', methods=['PUT'])
# @token_required_admin
# def update_quotation_status(current_user, quote_id):
def update_quote_status(quote_id):
    
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    quote = session.query(Quotation).filter_by(quote_id=quote_id).first()
    
    if not quote:
        return jsonify({'message' : 'No quote found!'})

    if quote.quote_status == "For Approval":
        quote.quote_status = "Rejected"
        quote.quote_validity = datetime.datetime.now() + timedelta(days=7)
        session.commit()

    return jsonify({'message' : 'The quotation has been rejected!'})

@app.route('/api/invoice/<invoice_no>', methods=['GET'])
# @token_required_admin
# def view_invoice(current_user, invoice_no):
def view_invoice(invoice_no):
    # if not current_user.admin:
        # return jsonify({'message' : 'Cannot perform that function!'})

    invoice = session.query(Invoice).filter_by(invoice_no=invoice_no).one()
    invoice_data = {}
    invoice_data['invoice_id'] = invoice.invoice_id
    invoice_data['invoice_no'] = invoice.invoice_no
    invoice_data['date_created'] = invoice.date_created
    invoice_data['quote_id'] = invoice.quote_id

    quotation = session.query(Quotation).filter_by(quote_id = invoice.quote_id).one()
    quotation_details = session.query(QuotationDetail).filter_by(quote_id = invoice.quote_id).all()
    invoice_data['price'] = 0
    for quotation_detail in quotation_details:
        invoice_data['price'] += quotation_detail.unit_price    
        
    client = session.query(Client).filter_by(client_id = quotation.client_id).one()
    invoice_data['client_name'] = client.client_firstname + " " + client.client_lastname

    return jsonify(invoice_data)

@app.route('/api/service', methods=['GET'])
def request_service():
    services = session.query(Service).all()
    output_data= {}
    
    service_cats = []
    for service in services:
        service_cats.append(service.service_cat)
    
    service_cats = list(set(service_cats))
    output_data['service_cats'] = service_cats
    for service_cat in service_cats:
        services = session.query(Service).filter_by(service_cat=service_cat).all()
        service_names = []
        for service in services:
            service_names.append(service.service_name)
            
        output_data[service_cat] = service_names

    return jsonify(output_data)

@app.route('/api/services/', methods=['GET'])
# @token_required_admin
# def get_all_services(current_user):
def get_all_services():
    services = session.query(Service).all()
    output_data= {}
    servicelist=[]
    for service in services:
        service_data={}
        service_data['service_name']=service.service_name
        service_data['service_cat']=service.service_cat
        service_data['base_price']=service.base_price
        output_data['services'] = service_data
        servicelist.append(service_data)
    output_data["services"] = servicelist

    return jsonify(output_data)

@app.route('/api/invoice/<quote_id>', methods=['POST'])
# @token_required_admin
# def create_invoice(current_user, quote_id):
def create_invoice(quote_id):
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})
    quote = session.query(Quotation).filter_by(quote_id=quote_id).first()
    if quote.quote_status != "Approved by both":
        return jsonify({"message": "Quotation has not yet been approved by both, cannot create invoice"})

    last_invoice_no = session.query(Invoice).count()
    
    invoice = Invoice(invoice_no = int(last_invoice_no + 1),
                      date_created = datetime.datetime.now(),
                      quote_id = quote_id,
                      paid = "Not Paid")
    session.add(invoice)
    session.commit()
    return jsonify({'message': 'New invoice created!'})

@app.route('/api/accounts', methods=['POST'])
# @token_required_admin
# def create_admin(current_user):
def create_admin():
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    data = request.get_json()
    password = "123456"
    hashed_password = generate_password_hash(password, method='sha256')

    new_admin = Admin(public_id=str(uuid.uuid4()),
                     admin_firstname=data['firstname'],
                     admin_lastname=data['lastname'],
                     admin_email=data['email'],
                     date_created=datetime.datetime.now(),
                     last_update=datetime.datetime.now(),
                     password=hashed_password, 
                     admin=True)
    session.add(new_admin)
    session.commit()

    return jsonify({'message': 'New admin created!'})

@app.route('/api/clients', methods=['POST'])
# @token_required_admin
# def create_client(current_user):
def create_client():
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    data = request.get_json()
    # password = (data['lastname'].replace(" ","")).lower() + "123"
    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_client = Client(public_id=str(uuid.uuid4()),  
                        client_firstname=data['firstname'],
                        client_lastname=data['lastname'],
                        client_email=data['email'],
                        company_name = data['company_name'],
                        client_landline="",
                        client_mobile=data['mobile'],
                        client_fax="",
                        client_address="",
                        date_created=datetime.datetime.now(),
                        date_updated=datetime.datetime.now(),
                        password=hashed_password, 
                        admin=False)
    session.add(new_client)
    session.commit()

    return jsonify({'message': 'New client created!'})

@app.route('/api/accounts/', methods=['GET'])
# @token_required_admin
# def get_all_admins(current_user):
def get_all_admins():
    
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})

    admins = session.query(Admin).all()
    
    output = []
    for admin in admins:
        admin_data = {}
        admin_data['public_id'] = admin.public_id
        admin_data['admin_firstname'] = admin.admin_firstname
        admin_data['admin_lastname'] = admin.admin_lastname
        admin_data['admin_email'] = admin.admin_email
        admin_data['public_id'] = admin.public_id
        admin_data['last_update'] = admin.last_update
        admin_data['date_created'] = admin.date_created
        admin_data['admin'] = admin.admin
        output.append(admin_data)
    return jsonify({'admins' : output})

@app.route('/api/invoice/<invoice_id>', methods=['PUT'])
def paid_invoice(invoice_id):
    invoice = session.query(Invoice).filter_by(invoice_id=invoice_id).first()
    invoice.paid = "Paid"
    session.commit()

    return jsonify({'message' : 'Client has paid'})

######################################LOGIN######################################################################


######################################USERS######################################################################
@app.route('/api/<public_id>/clients', methods=['GET'])
def client_profile(public_id):

    # projects = session.query(Project).all()
    client = session.query(Client).filter_by(public_id=public_id).one()
    quotations = session.query(Quotation).filter_by(client_id=client.client_id).all()

    output_data = {}
    client_list = []
    client_data = {}
    client_data['company_name'] = client.company_name
    client_list.append(client_data)

    quotation_list = []
    #resets every loop


    invoice_list = []
     #resets every loop

    for quotation in quotations:
        quotation_data = {} 
        quotation_data['quote_id'] = quotation.quote_id
        quotation_data['client_id'] = quotation.client_id
        quotation_data['quote_validity'] = quotation.quote_validity
        quotation_data['data_created'] = quotation.date_created
        quotation_data['is_package'] = quotation.is_package
        quotation_data['package_id'] = quotation.package_id
        quotation_data['last_updated'] = quotation.last_updated
        quotation_data['generated_id'] = quotation.generated_id
        quotation_data['quote_status'] = quotation.quote_status
        quotation_list.append(quotation_data)

        invoices = session.query(Invoice).filter_by(quote_id=quotation.quote_id).all()
        for invoice in invoices:
            quotation_details = session.query(QuotationDetail).filter_by(quote_id=invoice.quote_id).all()
            total = 0
            for quotation_detail in quotation_details:
                total += quotation_detail.unit_price * quotation_detail.qty
            invoice_data = {}            
            invoice_data['invoice_id'] = invoice.invoice_id
            invoice_data['invoice_no'] = invoice.invoice_no
            invoice_data['date_created'] = invoice.date_created
            invoice_data['quote_id'] = invoice.quote_id
            invoice_data['total price'] = total
            invoice_data['paid'] = invoice.paid
            invoice_list.append(invoice_data)


        output_data['client'] = client_list
        output_data['quotations'] = quotation_list
        output_data['invoices'] = invoice_list

    return jsonify(output_data)

@app.route('/api/<public_id>/quotation', methods=['POST'])
def request_quotation(public_id):
    data = request.get_json()
    generate = str(uuid.uuid4())
    client = session.query(Client).filter_by(public_id=public_id).first()
    is_package = True
    package_id = 0
    if data['package'] == "no package":
        is_package = False
        package_id = 1
    
    off = 0

    if data['promo'] != "":
        promo = (session.query(Promo).filter_by(priveledge_to=client.client_id)
                                     .filter_by(promo_name=data['promo'])).first()
        if not promo:
            return jsonify({'message': 'Not priveledge to use that promo'})
        else:
            off = promo.off


    new_quotation = Quotation(date_created = datetime.datetime.now(),
                              client_id = client.client_id,
                              quote_validity = datetime.datetime.now() + timedelta(days=7),
                              quote_status = "For Approval",
                              package_id = package_id,
                              is_package = is_package,
                              last_updated = datetime.datetime.now(),
                              generated_id = generate,
                              promo =  data['promo'])
    session.add(new_quotation)
    session.commit()
    quote = session.query(Quotation).filter_by(generated_id=generate).first()
    for desc, qty, service_type, service in zip(data['description'],data['qty'],data['type'],data['service']):
        print(service_type)
        print(service)
        # service_type = service name
        # service = service cat
        service = (session.query(Service).filter_by(service_name=service_type).filter_by(service_cat=service)).first()
        print(service.service_cat)
        if not service:
            return jsonify({'message':'no service'})

        new_quote_det = QuotationDetail(desc = desc,
                                        qty = qty,
                                        unit_price = (service.base_price * (1-off)),
                                        service_id = service.service_id,
                                        quote_id = quote.quote_id)
        session.add(new_quote_det)
        session.commit()
   
    return jsonify({'message': 'Requested new quotation!'})

@app.route('/api/<public_id>/quotation/<quote_id>', methods=['GET'])
def view_quotation(public_id, quote_id):
    client = session.query(Client).filter_by(public_id=public_id).first()
    quotation = session.query(Quotation).filter_by(quote_id=quote_id).first()
    output_data = {}
    total = 0
    
    if not client:
        return jsonify({'message': "no client"})

    if not quotation:
        return jsonify({'message': "no quotation"})

    output_data['quote_id'] = quotation.quote_id
    output_data['quote_validity'] = quotation.quote_validity
    output_data['date_created'] = quotation.date_created
    output_data['is_package'] = quotation.is_package
    output_data['quote_status'] = quotation.quote_status
    output_data['package_id'] = quotation.package_id
    output_data['last_updated'] = quotation.last_updated
    output_data['generated_id'] = quotation.generated_id
      
    quotation_details = session.query(QuotationDetail).filter_by(quote_id=quotation.quote_id).all()
      
    output_data['quotation_details'] = []
    for quotation_detail in quotation_details:
        quotation_details_data = {}
        quotation_details_data['desc'] = quotation_detail.desc
        quotation_details_data['qty'] = quotation_detail.qty
        quotation_details_data['unit_price'] = quotation_detail.unit_price
        quotation_details_data['service_id'] = quotation_detail.service_id
        quotation_details_data['quote_id'] = quotation_detail.quote_id
        output_data['quotation_details'].append(quotation_details_data)
        total += (quotation_detail.unit_price * quotation_detail.qty)

    
    invoice = session.query(Invoice).filter_by(quote_id=quote_id).first()
    if invoice:
        output_data['invoice_no'] = invoice.invoice_no
        output_data['invoice_id'] = invoice.invoice_id
        output_data['status'] = invoice.paid
        output_data['date_created'] = invoice.date_created
    else:
        output_data['invoice_no'] = ""
        output_data['invoice_id'] = ""
        output_data['status'] = ""
        output_data['date_created'] = ""
        
    
    output_data['total_sales'] = total
    output_data['company_name'] = client.company_name
        
    return jsonify(output_data)
    
@app.route('/api/<public_id>/quotation/<quote_id>', methods=['PUT'])
# def update_quotation(current_user, quote_id):
def update_quotation(public_id, quote_id):
    # if not current_user.admin:
    #     return jsonify({'message' : 'Cannot perform that function!'})
    quote = session.query(Quotation).filter_by(quote_id=quote_id).first()
    
    if not quote:
        return jsonify({'message' : 'No quote found!'})

    if quote.quote_status == "Approved by Admin":
        quote.quote_status = "Approved by both"
        session.commit()
        return jsonify({'message' : 'The quotation has been updated!'})
    else:
        return jsonify({'message' : "Quotation status has not yet been approved by admin"})
    
    # off = 0
    # if  data['promo']:
    #     promo = (session.query(Promo).filter_by(priveledge_to=quote.client_id)
    #                                  .filter_by(promo_name=data['promo']))
    #     if promo:
    #         off = promo.off
    #         quote.promo = data['promo']
    #         session.commit()
    #         quotation_details = session.query(QuotationDetail).filter_by(quote_id=quote_id).all()
    #         for quotation_detail in quotation_details:
    #             quotation_detail.unit_price = quotation_detail.unit_price * (1-off) 
    #             session.commit() 

    #     else:
    #         return jsonify({'message': 'Not priveledge to use that promo'})
        
        
@app.route('/api/login/admin', methods=['POST'])
def login_admin():
    data = request.get_json()

    if not data or not data['email'] or not data['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    admin = session.query(Admin).filter_by(admin_email=data['email']).first()

    if not admin:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(admin.password, data['password']):
        token = jwt.encode({'public_id' : admin.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        public_id = admin.public_id
        output_data = {}
        output_data['token'] = token.decode('UTF-8')
        output_data['public_id'] = public_id
        return jsonify(output_data)

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

@app.route('/api/login', methods=['GET','POST'])
def login():
    auth = request.get_json()

    # if not auth or not auth['email'] or not auth['password']:
    #     return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    client = session.query(Client).filter_by(client_email=auth['email']).first()
    admin = session.query(Admin).filter_by(admin_email=auth['email']).first()

    if not client:
        if not admin:
            return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    
    if client:
        if check_password_hash(client.password, auth['password']):
            token = jwt.encode({'public_id' : client.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
            # resp = make_response()
            # resp.headers.extend({'x-access-token' : client_data['token']})
            public_id = client.public_id
            output_data = {}
            output_data['token']= token.decode('UTF-8')
            output_data['public_id'] = public_id
            output_data['admin'] = client.admin

            return jsonify(output_data)

    if admin:
        if check_password_hash(admin.password, auth['password']):
            token = jwt.encode({'public_id' : admin.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
            # resp = make_response()
            # resp.headers.extend({'x-access-token' : client_data['token']})
            public_id = admin.public_id
            output_data = {}
            output_data['token']= token.decode('UTF-8')
            output_data['public_id'] = public_id
            output_data['admin'] = admin.admin
            return jsonify(output_data)

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    
if __name__ == '__main__':
    app.run(debug=True)