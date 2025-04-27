# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from mongoengine import Document, StringField, EmailField, ListField, ReferenceField
# from mongoengine import Document, StringField, EmailField, ListField,FileField, DateTimeField
# from werkzeug.security import generate_password_hash,check_password_hash
# import datetime

# class CustomUser(Document):
#     username = StringField(required=True, unique=True)
#     email = EmailField(required=True, unique=True)
#     password = StringField(required=True)  # Store hashed passwords securely
#     groups = ListField(StringField())  # Store group names as strings
#     user_permissions = ListField(StringField())  # Store permissions as strings

#     def set_password(self, raw_password):
#         """Hash password before saving (use your own hashing method)"""
#         self.password = generate_password_hash(raw_password)

#     def check_password(self, raw_password):
#         """Verify password hash"""
#         return check_password_hash(self.password, raw_password)

#     def __str__(self):
#         return self.username



# class Game(models.Model):
#     player_position = models.IntegerField(default=1)

#     def move_player(self, dice_value):
#         new_position = self.player_position + dice_value
#         snakes = {17: 7, 54: 34, 62: 19, 98: 79}
#         ladders = {3: 22, 6: 25, 11: 40, 60: 85}
        
#         if new_position in snakes:
#             new_position = snakes[new_position]
#         elif new_position in ladders:
#             new_position = ladders[new_position]
        
#         self.player_position = new_position if new_position <= 100 else self.player_position
#         self.save()

# class UploadedFile(Document):
#     file = FileField(required=True)  # Stores file in GridFS
#     uploaded_at = DateTimeField(default=datetime.datetime.utcnow)

#     def __str__(self):
#         return f"UploadedFile({self.id})"

from django.db import models
from django.contrib.auth.models import AbstractUser
from mongoengine import Document, StringField, EmailField, ListField, FileField, DateTimeField
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class CustomUser(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    groups = ListField(StringField())
    user_permissions = ListField(StringField())

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __str__(self):
        return self.username

# Django Game Model (for board game like Snakes and Ladders)
class Game(models.Model):
    player_position = models.IntegerField(default=1)

    def move_player(self, dice_value):
        new_position = self.player_position + dice_value
        snakes = {17: 7, 54: 34, 62: 19, 98: 79}  # Snakes positions
        ladders = {3: 22, 6: 25, 11: 40, 60: 85}  # Ladders positions
        
        # Check for snake or ladder and move player accordingly
        if new_position in snakes:
            new_position = snakes[new_position]
        elif new_position in ladders:
            new_position = ladders[new_position]
        
        # If the new position is within 100, update the player position
        self.player_position = new_position if new_position <= 100 else self.player_position
        self.save()

    def __str__(self):
        return f"Game({self.id}): Player Position {self.player_position}"


# MongoEngine Uploaded File Model (for file uploads using GridFS)
class UploadedFile(Document):
    file = FileField(required=True)  # Stores file in GridFS
    uploaded_at = DateTimeField(default=datetime.datetime.utcnow)

    def __str__(self):
        return f"UploadedFile({self.id})"


