import re
import io
import json
import os
import time
import zipfile

from flask import Flask, send_from_directory, request, redirect, url_for, session, send_file
import db

# ==================== Initialize app and login manager ====================
with open('config.json') as f:
    config = json.load(f)

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.secret_key = config['secret_key']

db = db.Database('config.json')
LOCKOUT_THRESHOLDS = config['security']['lockout-thresholds']

host = config['server_host']

organization_info = {"name": config['organization_name'], "email": config['organization_domain']}

if not config['security']['enabled']:
    print("WARNING: Security is disabled! This is not recommended for production use!")
    print("WARNING: Anybody can login with any email and password!")
    print("WARNING: To enable security, set 'enabled' to True in config.json")
    print("WARNING: To enable security, set 'enabled' to True in config.json")
    print("WARNING: To enable security, set 'enabled' to True in config.json")
    print("WARNING: YOU HAVE BEEN WARNED!")

if config['dev_mode']:
    print("INFO: Development mode is enabled! This is for only development use!")
    print("INFO: To disable development mode, set 'dev_mode' to False in config.json")
    print("Starting to build the vite app...")

    try:
        from fetch_build import fetch_build
        fetch_build()
    except ImportError:
        print("ERROR: Failed to build the vite app!")
        exit(1)

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
    if 'email' in session:
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

        email = request.form['email']
        password = request.form['password']

        if db.authenticate(email, password):
            session['email'] = email
            session.pop('failed_attempts', None)
            return {"success": True, "message": f"Succesfully logged in as {email}!"}
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
                return {"success": False, "message": f"Invalid email or password! ({session['failed_attempts']})"}

    elif action in ['org', 'org/']:
        return organization_info

    elif action in ['checkhandle', 'checkhandle/']:
        handle = request.args.get('handle')
        if handle in ['api', 'auth', 'sites', 'static', 'templates', 'userdata', 'admin']:
            return {"reserved": True, "exists": False}
        elif db.search_user(handle=handle) is None:
            return {"reserved": False, "exists": False}
        else:
            return {"reserved": False, "exists": True}

    elif action in ['authmail', 'authmail/']:
        email = request.args.get('email')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"success": False, "message": "Invalid email format!"}
        if not email.endswith("@" + config['organization_domain']):
            return {"success": False, "message": "Email outside organization!"}
        if not email.replace("@", "").replace(".", "").isalnum():
            return {"success": False, "message": "Email contains illegal characters!"}
        if db.search_user(email=email) is not None:
            return {"success": False, "message": "You already have an account! Try logging in."}
        if db.search_signup_token(email=email):
            return {"success": True, "message": "We recently sent you an email containing a link to sign up. Please check your inbox and spam folder!"}
        else:
            signup_token = db.signup_token(email=email, ip=request.remote_addr)
            print(signup_token)
            return {"success": True, "message": f"We have sent you an email to verify your email address ({email}). Please get the code from the email and enter it on the sign up form!"}

    elif action in ['signup', 'signup/']:

        code = request.form['code']
        email = request.form['email']

        print(code, email)

        valid_code, message = db.validate_signup_token(email=email, access_code=code)
        if not valid_code:
            return {"success": False, "message": message}

        handle = request.form['handle'].lower()
        password = request.form['password']
        if db.search_user(handle=handle) is not None:
            return {"success": False, "message": "Handle already exists!"}
        if not handle.isalnum():
            return {"success": False, "message": "Handle must be alphanumeric!"}
        if len(handle) > 20 or len(handle) < 3:
            return {"success": False, "message": "Handle must be between 3 and 20 characters!"}
        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters!"}
        if not any(char.isdigit() for char in password):
            return {"success": False, "message": "Password must have at least one digit!"}
        db.add_user(email=email, password=password, handle=handle, signup_ip=request.remote_addr)

        session['email'] = email

        return {"success": True, "message": ""}

    elif action in ['forgot', 'forgot/']:
        email = request.form['email']

        if db.search_user(email=email) is not None:
            token = db.password_reset_token(email=email)
            email_contents = f"""Hello!
To reset your password, please click the following link:
{host}/forgot?token={token}
This link will expire in 10 minutes.
            
If you did not request a password reset, please ignore this email."""
            print(email_contents)

        return {"success": True, "message": "If the email exists, we have sent you an email with a link to reset your password!"}

    elif action in ['reset', 'reset/']:
        token = request.form['token']
        password = request.form['password']
        if db.validate_password_reset_token(reset_token=token):
            if len(password) < 8:
                return {"success": False, "message": "Password must be at least 8 characters!"}
            if not any(char.isdigit() for char in password):
                return {"success": False, "message": "Password must have at least one digit!"}
            db.reset_password(reset_token=token, password=password)
            return {"success": True, "message": "Sucess!"}
        else:
            return {"success": False, "message": "Invalid reset token!"}

    else:
        return {"success": False, "message": "Invalid action!"}


# ==================== Home page routes ====================
# only allow logged in users to access the home page
@app.route('/home/', methods=['GET'])
def home():
    if 'email' in session:
        return send_from_directory('static', 'home.html')
    return redirect(url_for('login'))  # Redirect to login page if the user is not logged in


# ==================== Reset password routes ====================
@app.route('/forgot/', methods=['GET'])
def forgot():
    token = request.args.get('token')
    if token is None:
        return redirect(url_for('login'))
    else:
        if db.validate_password_reset_token(reset_token=token):
            return send_from_directory('static', 'forgot.html')
        else:
            return redirect(url_for('login'))


# ==================== API for authenticated users ====================
@app.route('/api/<path:action>', methods=['GET', 'POST'])
def api_route(action):
    if 'email' not in session:
        return {"success": False, "message": "You are not logged in! Go back to <a herf=\"/\">home</a>"}
    else:
        email = session['email']
        handle = db.search_user(email=email)['handle']

    if action == 'logout/' or action == 'logout':
        session.pop('email', None)
        return {"success": True}

    elif action == 'userinfo/' or action == 'userinfo':
        user = db.search_user(email=email)
        return {"success": True, "email": user['email'], "name": user['handle']}

    elif action == 'checkslug/' or action == 'checkslug':
        title = request.form['checkslug']
        if os.path.exists(os.path.join('userdata', handle, title)):
            return {"exists": True}
        else:
            return {"exists": False}

    elif action == 'getpages/' or action == 'getpages':
        # check the folder for the user
        user_dir = os.path.join('userdata', handle)
        if not os.path.exists(user_dir):
            return {"pages": []}
        # get all the folders in the user's folder
        pages = os.listdir(user_dir)
        # remove dot files
        pages = [page for page in pages if not page.startswith('.')]
        return {"pages": pages}

    elif action == 'download/' or action == 'download':
        # check the folder for the user
        slug = request.form.get('slug', '')
        user_dir = os.path.join('userdata', handle)
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
        slug = request.form.get('slug', '')
        user_dir = os.path.join('userdata', handle)
        slug_dir = os.path.join(user_dir, slug)
        if not os.path.exists(slug_dir):
            return {"success": False, "message": "Slug does not exist!"}
        # delete the folder
        import shutil
        shutil.rmtree(slug_dir)
        return {"success": True, "message": "Slug deleted successfully!"}

    elif action == 'upload/' or action == 'upload':
        slug = request.form.get('slug', '')
        user_dir = os.path.join('userdata', handle)
        slug_dir = os.path.join(user_dir, slug)

        if os.path.exists(slug_dir):  # check if slug exists
            return {"success": False, "message": "Slug already exists!"}
        if slug == '':  # check if slug is empty
            return {"success": False, "message": "Slug cannot be empty!"}
        if not slug.replace("-", "").isalnum():  # check if slug is alphanumeric
            return {"success": False, "message": "Slug must be alphanumeric!"}
        if len(slug) > 20:  # check if slug is less than 20 characters
            return {"success": False, "message": "Slug must be less than 20 characters!"}

        if 'file' not in request.files:  # Check if files are sent
            return {"success": False, "message": "No file part"}
        files = request.files.getlist('file')  # Get all files

        # Ensure the handle directory exists
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
