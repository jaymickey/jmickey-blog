from app import db

class User(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  first_name = db.Column(db.String(40))
  last_name = db.Column(db.String(40))
  username = db.Column(db.String(64), index = True, unique = True)
  email = db.Column(db.String(120), index = True, unique = True)
  password = db.Column(db.String(64))
  about_me = db.Column(db.String(200))
  
  def is_authenticated(self):
    return True
    
  def is_active(self):
    return True
    
  def is_anonymous(self):
    return False