from flask import Flask, render_template, request, session, redirect, make_response, url_for, flash, jsonify, g, abort, send_from_directory
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_session import Session
from flask_cors import CORS
from sassutils.wsgi import SassMiddleware
from base64 import b64encode
import os, requests, json, math, jsonpickle, uuid

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)
app.config['USE_SESSION_FOR_NEXT'] = True
app.config['SECRET_KEY'] = 'triglindustry'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] =43200
app.config['SESSION_COOKIE_NAME'] ='TRIGL-INDUSTRY'
app.secret_key = os.urandom(24)
app.config.from_object(__name__)
Session(app)
app.wsgi_app = SassMiddleware(app.wsgi_app, {
    'main': ('static/sass', 'static/css', '/static/css')
})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(401)
def unauthorized_page(e):
    return render_template('401.html'), 401

@app.errorhandler(500)
def internal_app_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    if 'token' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html', error=None)

@app.route('/login', methods=['POST'])
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

@app.route('/logout')
def logout():
    if session:
        session.pop('token', None)
        session.pop('username', None)
        session.pop('name', None)
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'token' in session:
        return render_template('dashboard.html')
    else:
        abort(401)

@app.route('/products', methods=['GET'])
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

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/products/add-product', methods=['GET', 'POST'])
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
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                return render_template('add-product.html', error='Invalid selected image')
            image = send_from_directory(app.config["UPLOAD_FOLDER"], filename)
            url = request.url_root
            image_url = str(url) + str(image)
            response = requests.post('https://hidden-ocean-47062.herokuapp.com/api/admin/products',
                          json={"name": productName, "subcategory": productSubcategory, "category": productCategory,
                                "brand":productBrand, "price": productSellingPrice, "stock": productQuantity,
                                "suppliers": "test", "variation": productVariation, "image": image_url, "tags": productTagsArray})
            print(response.status_code)
            return redirect(url_for('products'))
        return render_template('add-product.html', error=None)
    else:
        abort(401)

app.register_error_handler(404, page_not_found)
app.register_error_handler(401, unauthorized_page)
app.register_error_handler(500, internal_app_error)

if __name__=='__main__':
    app.run(host='localhost', port=8000, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
