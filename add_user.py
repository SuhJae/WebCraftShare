import json
import os
from argon2 import PasswordHasher


def load_users():
    """Load users from the JSON file."""
    with open('user.json', 'r') as file:
        return json.load(file)


def is_password_common(password):
    """Check if the password is in the list of common passwords."""
    with open('common_passwords.txt', 'r') as file:
        return password in file.read()


def get_username(users):
    """Prompt user for a valid username."""
    while True:
        username = input("Enter username: ")
        if not username.isalnum():
            print("Username must only contain alphanumeric characters. Please try again.")
        elif username.lower() in users:
            print("Username already exists. Please try again.")
        else:
            return username.lower()


def get_password():
    """Prompt user for a valid password and confirmation."""
    while True:
        password = input("Enter password: ")
        if len(password) < 10:
            print("Password is too short. It must be at least 10 characters long. Please try again.")
        elif is_password_common(password):
            print("Password is too common. Please try again.")
        else:
            password_confirm = input("Confirm password: ")
            if password != password_confirm:
                print("Passwords do not match. Please try again.")
            else:
                return password


def main():
    users = load_users()

    username = get_username(users)
    password = get_password()

    salt = os.urandom(32).hex()
    hashed_password = PasswordHasher().hash(password + salt)

    user_data = {
        "hash": hashed_password,
        "salt": salt
    }

    # Add user to users and save to the JSON file
    users[username] = user_data
    with open('user.json', 'w') as file:
        json.dump(users, file, indent=4)


if __name__ == "__main__":
    main()
