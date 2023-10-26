class User:
    def __init__(self, user_id, username, email, password):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return f"User ID: {self.user_id}, Username: {self.username}, Email: {self.email}"

    # Additional methods for user-related functionality can be added here
    def change_password(self, new_password):
        self.password = new_password

    # You can also define methods for database operations (e.g., saving and retrieving users)
    # These methods would typically interact with your database using an ORM or raw SQL queries
