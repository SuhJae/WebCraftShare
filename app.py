import json
import os
import time

from flask import Flask, send_from_directory, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from auth import Authenticator

# ==================== Initialize app and login manager ====================
config = json.load(open('config.json'))
app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.secret_key = config['secret_key']

authenticator = Authenticator()
MAX_TRIALS = 3
LOCKOUT_DURATION = 60


# ==================== Login manager callback functions ====================


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    return send_from_directory('static', 'html/login.html')


@app.route('/home/')
def home():
    if 'username' in session:
        return send_from_directory('static', 'html/home.html')
    return redirect(url_for('login'))  # Redirect to login page if the user is not logged in


@app.route('/auth/<path:action>', methods=['POST', 'GET'])
def auth_route(action):
    if action in ['authenticate', 'authenticate/']:

        # Check if user is locked out
        if session.get('lockout_time'):
            time_elapsed = time.time() - session['lockout_time']
            if time_elapsed < LOCKOUT_DURATION:
                return {"success": False, "message": "Too many failed attempts. Please try again later."}
            else:
                # Reset after lockout duration
                session.pop('lockout_time', None)
                session.pop('failed_attempts', None)

        username = request.form['username']
        password = request.form['password']
        time.sleep(1)

        if authenticator.authenticate(username, password):
            session['username'] = username  # Storing the username in session
            # Reset the failed attempts on successful login
            session.pop('failed_attempts', None)
            return {"success": True, "message": f"Welcome {session['username']}!"}
        else:
            # Increment the failed attempts counter
            session['failed_attempts'] = session.get('failed_attempts', 0) + 1
            if session['failed_attempts'] >= MAX_TRIALS:
                session['lockout_time'] = time.time()
                return {"success": False, "message": "Too many failed attempts. Please try again later."}
            else:
                return {"success": False, "message": "Invalid username or password!"}

    elif action in ['checkuser', 'checkuser/']:
        username = request.args.get('username')
        if authenticator.user_exists(username):
            return {"exists": True}
        else:
            return {"exists": False}

    else:
        return {"success": False, "message": "Invalid action!"}


@app.route('/api/<path:action>', methods=['GET', 'POST'])
def api_route(action):
    if 'username' not in session:
        return {"success": False, "message": "You are not logged in!"}

    if action == 'logout/' or action == 'logout':
        time.sleep(0.3)
        session.pop('username', None)
        return {"success": True}

    elif action == 'userinfo/' or action == 'userinfo':
        username = session['username']
        return {"username": username}

    elif action == 'checkslug/' or action == 'checkslug':
        title = request.form['checkslug']
        username = session['username']
        if os.path.exists(os.path.join('userdata', username, title)):
            return {"exists": True}
        else:
            return {"exists": False}

    elif action == 'upload/' or action == 'upload':
        username = session['username']
        slug = request.form.get('slug', '')
        user_dir = os.path.join('userdata', username)
        slug_dir = os.path.join(user_dir, slug)

        if os.path.exists(slug_dir):  # check if slug exists
            return {"success": False, "message": "Slug already exists!"}
        if slug == '':  # check if slug is empty
            return {"success": False, "message": "Slug cannot be empty!"}
        if not slug.isalnum():  # check if slug is alphanumeric
            return {"success": False, "message": "Slug must be alphanumeric!"}
        if len(slug) > 20:  # check if slug is less than 20 characters
            return {"success": False, "message": "Slug must be less than 20 characters!"}

        time.sleep(1)

        if 'file' not in request.files:  # Check if files are sent
            return {"success": False, "message": "No file part"}
        files = request.files.getlist('file')  # Get all files

        # Ensure the username directory exists
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # Create (or ensure existence of) the slug directory inside the user's directory
        if not os.path.exists(slug_dir):
            os.makedirs(slug_dir)

        # Save each file
        for file in files:
            filename = secure_filename(file.filename)
            print(filename)
            file_path = os.path.join(slug_dir, filename)
            file.save(file_path)
        return {"success": True, "message": "Files uploaded successfully!"}

    else:
        return {"success": False, "message": "Invalid action!"}


@app.route('/sites/<path:path>')
def serve_site(path):
    print(path)  # jay/hello/ -> jay/hello/index.html
    if path.endswith('/'):
        path += 'index.html'
    return send_from_directory('userdata', path)


if __name__ == '__main__':
    app.run(debug=True)
