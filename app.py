from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import numpy as np
import tensorflow as tf
import os
from werkzeug.utils import secure_filename
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import base64
import cv2


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

MODEL_PATH = './model/fingerprint_model.h5'
model = tf.keras.models.load_model(MODEL_PATH)
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

def preprocess_fingerprint(base64_data):
    try:
        # Decode Base64
        image_data = base64.b64decode(base64_data)
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)  # Read as grayscale

        # Resize to (64, 64) as required by the CNN model
        img = cv2.resize(img, (128, 128))

        # Convert grayscale (1 channel) to RGB (3 channels)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        # Normalize pixel values (0 to 1)
        img = img / 255.0

        # Expand dimensions to match CNN input shape (batch_size, height, width, channels)
        img = np.expand_dims(img, axis=0)  # Add batch dimension

        print("Processed image shape:", img.shape)  # Debugging
        return img

    except Exception as e:
        print("Error processing image:", str(e))
        return None


@app.before_request
def log_request_info():
    print("\n[LOG] Received request:")
    print("URL:", request.url)
    print("Method:", request.method)
    print("Headers:", request.headers)
    print("Data:", request.get_data())


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid Credentials', 'danger')
    return render_template('login.html')


# Route for Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None  # Variable for storing error messages
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error_message = "Email already exists! Please use another email."
            return render_template('register.html', error_message=error_message)

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', error_message=error_message)



@app.route('/user')
def get_user():
    if current_user.is_authenticated:
        return jsonify({"username": current_user.username})


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/about')
@login_required
def about():
    return render_template('about.html')


# Home Page (Requires Login)
@app.route('/index')
@login_required
def index():
    return render_template('index.html')


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    try:
        data = request.get_json()
        print("Received JSON:", data)

        if not data or "image" not in data:
            print("[ERROR] No image received")
            return jsonify({"error": "No image received"}), 400

        image = preprocess_fingerprint(data["image"])
        if image is None:
            print("[ERROR] Invalid image")
            return jsonify({"error": "Invalid image"}), 400

        predictions = model.predict(image)
        blood_group = BLOOD_GROUPS[np.argmax(predictions)]

        print("[SUCCESS] Predicted Blood Group:", blood_group)
        return jsonify({"blood_group": blood_group})

    except Exception as e:
        print("[ERROR] Internal Server Error:", str(e))
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Password reset link sent to your email.', 'info')
        else:
            flash('Email not found!', 'danger')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # You will implement password reset functionality with a token here
    return render_template('reset_password.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
