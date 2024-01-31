from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
import matplotlib
from snmp import graph , get_name , history , database
from dal import *
from weather import get_weather_forecast, plot_temperature , extract_hourly_data , make_temperature_prediction
matplotlib.use('Agg')
from flask_session import Session
from models import *
from flask_jwt_extended import JWTManager ,create_access_token
import hashlib

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
jwt = JWTManager(app)
app.secret_key = '4@2@3@1@6@4@2@1@'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def home():
    if 'email' in session:
        return redirect(url_for('devices'))
    else:
        return redirect(url_for('login'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Hash the entered password
        hashed_entered_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        user_info = UserDao.authenticate_user(email, hashed_entered_password)
        
        if user_info:
            user = User(**user_info)
            session['email'] = user.username  
            session['id'] = user.id

            access_token = create_access_token(identity=user.id)
            
            response = redirect(url_for('home'))
            response.set_cookie('access_token_cookie', value=access_token, httponly=True)

            return response

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('User Name')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        UserDao.create_user(username, hashed_password, email)

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/signup.html')


@app.route('/weather/<ip>')
def weather(ip):
    device = DeviceDao.get_device_by_ip(ip)
    weather_data = get_weather_forecast(device.latitude, device.longitude)

    if weather_data:
        image_base64 = plot_temperature(weather_data)
        timestamps_next, temperatures = extract_hourly_data(weather_data)
        image = make_temperature_prediction(timestamps_next, temperatures)
        return render_template('weather.html', image_base64=image_base64 ,image=image, device= device)
    else:
        return "Failed to fetch weather data."
    


@app.route('/devices')
def devices():
    if 'id' not in session:
        flash('Error: User not logged in.', 'error')
        return redirect(url_for('auth/login.html'))

    devices = DeviceDao.get_devices_by_user(session['id'])
    return render_template('devices.html', devices = devices)


@app.route('/add_device', methods=['POST'])
def add_device():
    ip_address = request.form.get('ip_address')
    mac_address = request.form.get('mac_address')
    longitude = float(request.form.get('longitude'))
    latitude = float(request.form.get('latitude'))
    
    name = get_name(ip_address)
    
    if name == 'None' or name == None:
        flash('Error: The provided IP address is invalid or does not exist.', 'error')
        return redirect(url_for('devices'))
    
    DeviceDao.create_device(session['id'] , name , ip_address , mac_address , longitude, latitude)

    return redirect(url_for('devices'))

@app.route('/device/<ip>')
def device(ip):
    labels = []
    usage = []
    image_base64 , labels , usage = graph(ip)
    database(ip , labels , usage)
    image = history(ip)
    return render_template('device_details.html', image_base64 = image_base64 , image = image , ip = ip)

@app.route('/iot/<ip>')
def iot(ip):
    device = DeviceDao.get_device_by_ip(ip)
    if device:
        return render_template('iot.html', device = device)
    else:
        flash(f"Device with MAC address {ip} not found.", 'error')
        return redirect(url_for('devices'))
    
@app.route('/iot/temperature', methods=['POST'])
def handle_temperature_data():
    if request.method == 'POST':
        data = request.json
        mac_address = data.get('mac_address')
        temperature = data.get('temperature')


        return jsonify({"message": "Temperature data received successfully"}), 200
