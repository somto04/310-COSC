class user:
    penaltiesCount = 0

    def __init__(self, userId, name, age, email, username, password):
        self.userId = userId
        self.name = name
        self.age = age
        self.email = email
        self.username = username
        self.password = password

    # user getters
    def get_userId(self):
        return self.userId
    
    def get_name(self):
        return self.name
    
    def get_age(self):
        return self.age
    
    def get_email(self):
        return self.email
    
    def get_username(self):
        return self.username
    
    def get_password(self):
        return self.password
    
    def get_penaltiesCount(self):
        return self.penaltiesCount
    
    # user setters
    
    def set_userId(self, userId):
        self.userId = userId

    def set_name(self, name):
        self.name = name
    
    def set_age(self, age):
        self.age = age
    
    def set_email(self, email):
        self.email = email

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    def set_penaltiesCount(self, penaltiesCount):
        self.penaltiesCount = penaltiesCount


