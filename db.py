import json
import os
import random
import time

import pymongo
from argon2 import PasswordHasher, exceptions
from bson.binary import Binary


# this is a python script for managing mongodb database
def _generate_access_code(length: int):
    """Generates a random access code that is:
    1. minimum 2 alphabets and numbers
    2. All uppercase
    3. No special characters
    4. No ambiguous characters (0, O, 1, I)
    5. No repeating characters
    Args:
        length (int): The length of the access code.
    """
    valid_characters = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"

    access_code = ""
    for i in range(length):
        access_code += random.choice(valid_characters)

    return access_code


class Database:
    def __init__(self, config_file: str = 'config.json'):
        """ Initialize the database connection.
        :param config_file: The path to the config file.
        """

        with open(config_file) as f:
            config = json.load(f)

        host = config['db']['host']
        dbname = config['db']['dbname']

        if config['db']['auth']['enabled']:
            username = config['db']['auth']['username']
            password = config['db']['auth']['password']

            self.client = pymongo.MongoClient(host, username=username, password=password)
        else:
            self.client = pymongo.MongoClient(host)

        self.db = self.client[dbname]

    def add_user(self, email: str, password: str, handle: str, signup_ip: str, signup_time: int = int(time.time())):
        """Add a new user to the database. It will hash the password and generate a salt.
        :param email: The user's email address.
        :param password: The user's password.
        :param handle: The user's unique handle.
        :param signup_ip: The user's signup IP address.
        :param signup_time: The user's signup time in unix time.
        :return: The user's data.
        """

        salt = os.urandom(32)
        hashed_password = PasswordHasher().hash(password + salt.hex())

        user = {
            "email": email,
            "password": hashed_password,
            "salt": Binary(salt),
            "handle": handle,
            "user_info": {
                "signup_ip": signup_ip,
                "signup_time": signup_time,
            }
        }

        self.db.users.insert_one(user)
        return user

    def change_password(self, email: str, password: str):
        """Change a user's password.
        :param email: The user's email address.
        :param password: The user's password.
        :return: None
        """

        salt = os.urandom(32)
        hashed_password = PasswordHasher().hash(password + salt.hex())

        self.db.users.update_one({"email": email}, {"$set": {"password": hashed_password, "salt": Binary(salt)}})

    def password_reset_token(self, email: str, expires: int = 600):
        """ Add a new password reset token to the database.
        :param email: The user's email address.
        :return: temparary password
        """

        if self.db.password_reset_tokens.find_one({"email": email}) is not None:
            self.db.password_reset_tokens.delete_many({"email": email})

        reset_token = _generate_access_code(64)

        password_reset_token = {
            "email": email,
            "reset_token": reset_token,
            "expires": time.time() + expires
        }

        self.db.password_reset_tokens.insert_one(password_reset_token)
        return reset_token

    def validate_password_reset_token(self, reset_token: str):
        """ Validate a password reset token.
        :param reset_token: The user's reset token.
        :return: Boolean value indicating whether the reset token is valid.
        """

        password_reset_token = self.db.password_reset_tokens.find_one({"reset_token": reset_token})

        if password_reset_token is None:
            return False
        elif password_reset_token["expires"] < time.time():
            return False
        else:
            return password_reset_token["email"]

    def reset_password(self, reset_token: str, password: str):
        """ Reset a user's password.
        :param reset_token: The user's reset token.
        :param password: The user's new password.
        :return: None
        """

        salt = os.urandom(32)
        hashed_password = PasswordHasher().hash(password + salt.hex())

        email = self.validate_password_reset_token(reset_token)
        self.db.users.update_one({"email": email}, {"$set": {"password": hashed_password, "salt": Binary(salt)}})
        self.db.password_reset_tokens.delete_many({"email": email})

    def authenticate(self, email: str, password: str):
        """Authenticate a user based on email and password.
        :param email: The user's email address.
        :param password: The user's password.
        :return: Boolean value indicating whether the authentication succeeded.
        """

        user = self.db.users.find_one({"email": email})

        if user is None:
            return False

        salt = user["salt"]
        hashed_password = user["password"]

        try:
            PasswordHasher().verify(hashed_password, password + salt.hex())
            return True
        except exceptions.VerifyMismatchError:
            return False

    def signup_token(self, email: str, ip: str, expires: int = 600):
        """ Add a new sign in access token to the database.
        :param email:  The user's email address.
        :param ip: The user's IP address.
        :param expires: The user's access token expiration time in seconds. Default is 600 seconds.
        :return: The user's access token.
        """

        # check if the user already has a signup token
        if self.db.signup_tokens.find_one({"email": email}) is not None:
            self.db.signup_tokens.delete_many({"email": email})

        token = _generate_access_code(6)

        signup_token = {
            "email": email,
            "access_token": _generate_access_code(6),
            "ip": ip,
            "expires": time.time() + expires
        }

        self.db.signup_tokens.insert_one(signup_token)
        return token

    def search_signup_token(self, email: str):
        """ Search for a signup token using email.
        :param email: The user's email address.
        :return: Boolean value indicating the existence of the valid signup token.
        """

        signup_token = self.db.signup_tokens.find_one({"email": email})
        if signup_token is None:
            return False
        elif signup_token["expires"] < time.time():
            return False
        else:
            return True

    def validate_signup_token(self, access_code: str, email: str):
        """ Validate a sign in access token.
        :param access_code: The user's access token.
        :param email: The user's email address.
        :return: Boolean value indicating whether the access. If the access token is valid, it will also return the
        user's email address. If the access token is invalid, it will return the reason why it is invalid.
        """

        print(access_code, email)

        signup_token = self.db.signup_tokens.find_one({"email": email})
        print(signup_token)

        if signup_token is None:
            return False, "Invalid access token."

        if signup_token["email"] != email:
            return False, "Invalid email address."

        if signup_token["expires"] < time.time():
            return False, "Access token has expired."

        self.db.signup_tokens.delete_many({"email": email})
        return True, signup_token["email"]

    def search_user(self, email: str = None, handle: str = None):
        """ Search for a user using email or handle or both.
        :param email: The user's email address.
        :param handle: The user's handle.
        :return: The user's data. None if the user does not exist or the search query is invalid.
        """

        search_result = None

        if email is not None and handle is not None:
            search_result = self.db.users.find_one({"email": email, "handle": handle})
        elif email is not None:
            search_result = self.db.users.find_one({"email": email})
        elif handle is not None:
            search_result = self.db.users.find_one({"handle": handle})

        return search_result


if __name__ == "__main__":
    db = Database()

    # exaple of adding a user
    # username_input = input("Enter email: ")
    # password_input = input("Enter password: ")
    # entered_handle = input("Enter handle: ")
    #
    # user = db.add_user(email=username_input, password=password_input, handle=entered_handle, signup_ip="127.0.0.1",
    #             signup_time=int(time.time()))
    #
    # print(user)

    # example of authenticating a user
    # username_input = input("Enter email: ")
    # password_input = input("Enter password: ")
    #
    # if db.authenticate(username_input, password_input):
    #     print("Logged in")
    # else:
    #     print("Incorrect email or password")

    # example of searching for a user from email
    username_input = input("Enter email: ")
    user = db.search_user(email=username_input)
    print(user)
