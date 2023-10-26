from your_status_module import Status  # Import the Status enum

class Alert:
    def __init__(self, alert_id, location, image, time, user_id, project_id, status):
        self.alert_id = alert_id  # Unique identifier for the alert
        self.location = location  # Description of the alert's location
        self.image = image        # Path or URL to the associated image
        self.time = time          # Timestamp when the alert was generated
        self.status = status      # Current status of the alert (use the Status enum)

    def __str__(self):
        return f"Alert ID: {self.alert_id}, Location: {self.location}, Time: {self.time}, Status: {self.status}"

    # Additional methods for alert-related functionality can be added here
    def update_status(self, new_status):
        self.status = new_status

    # You can also include methods for database operations (e.g., saving and retrieving alerts)
    # These methods would typically interact with your database using an ORM or raw SQL queries
