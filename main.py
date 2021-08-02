from flask import Flask, render_template, request, session, redirect, make_response, url_for, flash, jsonify, g, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS
from base64 import b64encode
import os, requests, json, math, jsonpickle, uuid

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg'}

server = Flask(__name__)
server.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@server.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@server.errorhandler(401)
def unauthorized_page(e):
    return render_template('401.html'), 401

@server.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@server.route('/')
def index():
    if 'token' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html', error=None)

@server.route('/login', methods=['POST'])
def login():
    session.pop('token', None)
    session.pop('username', None)
    session.pop('name', None)
    username = request.form['inputUsername']
    password = request.form['inputPassword']
    response = requests.post('https://hidden-ocean-47062.herokuapp.com/api/login', json={'username': username, 'password': password})
    print(response.status_code)
    if response.status_code == 200:
        data = json.loads(response.text)
        session['token'] = data['token']
        session['username'] = data['username']
        session['name'] = data['name']
        flash('You were successfully logged in')
        return redirect(url_for('dashboard'))
    elif response.status_code == 401:
        return render_template('index.html', error=response.status_code)
    elif response.status_code == 500:
        return render_template('500.html')

@server.route('/logout')
def logout():
    if session:
        session.pop('token', None)
        session.pop('username', None)
        session.pop('name', None)
    return redirect(url_for('index'))

@server.route('/dashboard', methods=['GET'])
def dashboard():
    if 'token' in session:
        return render_template('dashboard.html')
    else:
        abort(401)

@server.route('/products', methods=['GET'])
def products():
    if 'token' in session:
        return render_template('products.html')
    else:
        abort(401)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES

@server.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(server.config["UPLOAD_FOLDER"], name)

@server.route('/products/add-product', methods=['GET', 'POST'])
def add_product():
    if 'token' in session:
        if request.method == 'POST':
            productName = request.form['productName']
            productDescription = request.form['productDescription']
            productCategory = request.form['productCategory']
            productSubcategory = request.form['productSubcategory']
            productBrand = request.form['productBrand']
            productQuantity = request.form['productQuantity']
            productVariation = request.form['productVariation']
            productSellingPrice = request.form['productSellingPrice']
            productTags = request.form['productTags']
            productTagsArray = productTags.split(",")
            # check if the post request has the file part
            print(request.files)
            if 'file' not in request.files:
                return render_template('add-product.html', error='No selected file')
            file = request.files['file']
            print(file)
            print(file.filename)
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                return render_template('add-product.html', error='No selected file')
            if file and allowed_image(file.filename):
                filename = str(uuid.uuid4())+'.jpeg'
                file.save(os.path.join(server.config['UPLOAD_FOLDER'], filename))
            else:
                return render_template('add-product.html', error='Invalid selected image')
            image = send_from_directory(server.config["UPLOAD_FOLDER"], filename)
            requests.post('https://hidden-ocean-47062.herokuapp.com/api/admin/products',
                          json={"name": productName, "subcategory": productSubcategory, "category": productCategory,
                                "brand":productBrand, "price": productSellingPrice, "stock": productQuantity,
                                "suppliers": "", "variation": productVariation, "image": image})
            return redirect(url_for('products'))
        return render_template('add-product.html', error=None)
    else:
        abort(401)




CORS(server)
server.register_error_handler(404, page_not_found)
server.register_error_handler(401, unauthorized_page)
server.register_error_handler(500, internal_server_error)
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['USE_SESSION_FOR_NEXT'] = True
server.config['CORS_HEADERS'] = 'Content-Type'
server.config['SECRET_KEY'] = 'thisissecret'
server.secret_key = os.urandom(24)

if __name__=='__main__':
    server.run(host='localhost', port=8000, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
