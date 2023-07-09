from flask_login import UserMixin

import db


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

        # Create db entry for users that do not have a database entry
        if not db.get_user(id_):
            self.create(id_, name, email, profile_pic)

    @staticmethod
    def get(id_):
        user_attributes = db.get_user(id_)
        if not user_attributes:
            return None
        return User(*user_attributes)

    @staticmethod
    def create(id_, name, email, profile_pic):
        db.create_user(id_, name, email, profile_pic)
