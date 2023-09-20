import io
import json
import os
import time
import zipfile

from flask import Flask, send_from_directory, request, redirect, url_for, session, send_file
from auth import Authenticator
from flask_cors import CORS

# ==================== Initialize app and login manager ====================
with open('config.json') as f:
    config = json.load(f)
app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.secret_key = config['secret_key']

CORS(app, resources={r"/api/*": {"origins": "*"}}) # this, when developing frontend using vuejs it allows /api/
# to be accessed from any origin

authenticator = Authenticator()
LOCKOUT_THRESHOLDS = config['security']['lockout-thresholds']

if not config['security']['enabled']:
    print("WARNING: Security is disabled! This is not recommended for production use!")
    print("WARNING: Anybody can login with any username and password!")
    print("WARNING: To enable security, set 'enabled' to True in config.json")
    print("WARNING: To enable security, set 'enabled' to True in config.json")
    print("WARNING: To enable security, set 'enabled' to True in config.json")
    print("WARNING: YOU HAVE BEEN WARNED!")


# ==================== Lockdown functions ====================
def get_lockout_duration(failed_attempts):
    """Return lockout duration based on the number of failed attempts."""
    for threshold, duration in sorted(LOCKOUT_THRESHOLDS.items(), key=lambda x: int(x[0])):
        if failed_attempts >= int(threshold):
            return duration
    return 0


# ==================== Login manager callback functions ====================
@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    return send_from_directory('static', 'index.html')


# ==================== Authentication routes ====================
@app.route('/auth/<path:action>', methods=['POST', 'GET'])
def auth_route(action):
    if not config['security']['enabled']:
        # If security is not enabled, let's allow authentication always
        return {"success": True, "message": "Security is disabled."}

    if action in ['authenticate', 'authenticate/']:
        if session.get('lockout_time'):
            time_elapsed = time.time() - session['lockout_time']
            lockout_duration = get_lockout_duration(session.get('failed_attempts', 0))

            if lockout_duration == -1:  # Permanent lockout
                return {"success": False,
                        "message": "Your account is locked permanently due to too many failed attempts."}

            if time_elapsed < lockout_duration:
                print(lockout_duration)
                return {"success": False, "message": "Too many failed attempts. Please try again later."}
            else:
                session.pop('lockout_time', None)
                session.pop('failed_attempts', None)

        username = request.form['username']
        password = request.form['password']
        time.sleep(1)

        if authenticator.authenticate(username, password):
            session['username'] = username
            session.pop('failed_attempts', None)
            return {"success": True, "message": f"Welcome {session['username']}!"}
        else:
            session['failed_attempts'] = session.get('failed_attempts', 0) + 1
            lockout_duration = get_lockout_duration(session['failed_attempts'])
            if lockout_duration > 0:
                session['lockout_time'] = time.time()
                if lockout_duration == -1:  # Permanent lockout
                    return {"success": False,
                            "message": "Your account is locked permanently due to too many failed attempts."}
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


# ==================== Home page routes ====================
# only allow logged in users to access the home page
@app.route('/home/')
def home():
    if 'username' in session:
        return send_from_directory('static', 'home.html')
    return redirect(url_for('login'))  # Redirect to login page if the user is not logged in


# ==================== API for authenticated users ====================
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

    elif action == 'getpages/' or action == 'getpages':
        # check the folder for the user
        username = session['username']
        user_dir = os.path.join('userdata', username)
        if not os.path.exists(user_dir):
            return {"pages": []}
        # get all the folders in the user's folder
        pages = os.listdir(user_dir)
        # remove dot files
        pages = [page for page in pages if not page.startswith('.')]
        return {"pages": pages}

    elif action == 'download/' or action == 'download':
        # check the folder for the user
        username = session['username']
        slug = request.form.get('slug', '')
        user_dir = os.path.join('userdata', username)
        slug_dir = os.path.join(user_dir, slug)
        if not os.path.exists(slug_dir):
            return {"success": False, "message": "Slug does not exist!"}

        # get all the files in the user's folder
        files = os.listdir(slug_dir)
        files = [file for file in files if not file.startswith('.')]
        # save the zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                file_path = os.path.join(slug_dir, file)
                zipf.write(file_path, file)

        # Move buffer position to the beginning after writing
        zip_buffer.seek(0)
        # Return the zip file
        return send_file(zip_buffer, download_name=f"{slug}-webfile.zip", as_attachment=True,
                         mimetype='application/zip')

    elif action == 'delete/' or action == 'delete':
        username = session['username']
        slug = request.form.get('slug', '')
        user_dir = os.path.join('userdata', username)
        slug_dir = os.path.join(user_dir, slug)
        if not os.path.exists(slug_dir):
            return {"success": False, "message": "Slug does not exist!"}
        # delete the folder
        import shutil
        shutil.rmtree(slug_dir)
        return {"success": True, "message": "Slug deleted successfully!"}


    elif action == 'upload/' or action == 'upload':
        username = session['username']
        slug = request.form.get('slug', '')
        user_dir = os.path.join('userdata', username)
        slug_dir = os.path.join(user_dir, slug)

        if os.path.exists(slug_dir):  # check if slug exists
            return {"success": False, "message": "Slug already exists!"}
        if slug == '':  # check if slug is empty
            return {"success": False, "message": "Slug cannot be empty!"}
        if not slug.replace("-", "").isalnum(): # check if slug is alphanumeric
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
            if file.filename.startswith('.'):  # Skip dot files
                continue

            # Split the path and discard the first component, which is the folder name
            parts = file.filename.split(os.path.sep)[1:]

            # Join the parts again to get the new relative path without the folder name
            new_relative_path = os.path.join(*parts)

            file_path = os.path.join(slug_dir, new_relative_path)

            # Create necessary directories for the current file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

        return {"success": True, "message": "Files uploaded successfully!"}
    else:
        return {"success": False, "message": "Invalid action!"}


# ==================== Serve user sites ====================
@app.route('/sites/<user>/<slug>/', defaults={'path': ''})
@app.route('/sites/<user>/<slug>/<path:path>')
def serve_site(user, slug, path=''):
    if not path:
        path = 'index.html'
        # check if file exists
        if not os.path.exists(os.path.join('userdata', user, slug, path)):
            # try to serve first html file
            for file in os.listdir(os.path.join('userdata', user, slug)):
                if file.endswith('.html'):
                    path = file
                    break

    if os.path.exists(os.path.join('userdata', user, slug, path)):
        return send_from_directory(os.path.join('userdata', user, slug), path)
    else:
        return send_from_directory('static', '404.html')


# ==================== Run the app ====================
if __name__ == '__main__':
    app.run(debug=False, port=5001)
