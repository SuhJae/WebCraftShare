import json
from argon2 import PasswordHasher, exceptions


class Authenticator:
    def __init__(self, user_file='user.json'):
        self.user_file = user_file
        self.users = self._load_users()

    def _load_users(self):
        """Load users from the JSON file."""
        with open(self.user_file, 'r') as file:
            return json.load(file)

    def authenticate(self, username, password):
        """Authenticate a user based on username and password."""
        username = username.lower()  # Convert username to lowercase for consistent lookup

        if username not in self.users:
            return False  # Username does not exist

        user_data = self.users[username]
        stored_hash = user_data["hash"]
        salt = user_data["salt"]

        try:
            # Verify password hash
            PasswordHasher().verify(stored_hash, password + salt)
            return True  # Authentication succeeded
        except exceptions.VerifyMismatchError:
            return False  # Password does not match

    def user_exists(self, username):
        """Check if a user exists."""
        username = username.lower()
        return username in self.users


# Example usage:
if __name__ == '__main__':
    authenticator = Authenticator()

    # Check authentication (for demonstration purposes)
    username_input = input("Enter username: ")
    password_input = input("Enter password: ")
    if authenticator.authenticate(username_input, password_input):
        print(f"Logged in as {username_input}")
    else:
        print("Incorrect username or password")
