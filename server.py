from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///AuthDatabase.sqlite3'
db = SQLAlchemy(app)

class Account(db.Model):
    ID = db.Column(db.Integer, primary_key = True)
    UserName = db.Column(db.String(100))
    Password = db.Column(db.String(100))
    def __init__(self,UserName,Password):
        self.UserName = UserName
        self.Password = Password
    
@app.route('/Auth', methods = ["GET","POST"])
def AuthUser():
    if request.method == 'POST':
        UserName = None
        Password = None
        Task = None
        DataPairs = request.get_data().decode("utf-8").split("&")
        for Pair in DataPairs:
            Pair = Pair.split("=")
            Key = Pair[0]
            Value = Pair[1]
            if Key == "username":
                UserName = Value
            elif Key == "password":
                Password = Value
            elif Key == "function":
                Task = Value
            else:
                return "Malformed JSON input - make sure to follow the planning document",400
                
        if None in [UserName,Password,Task]:
            return "Missing key account data - make sure to follow the planning document",400
        
        if Task == "creation":
            try:
                db.session.add(Account(UserName,Password))
                db.session.commit()
            except:
                return "Unable to create account", 400
            return "Account created for {}".format(UserName),200
        elif Task == "deletion":
            try:
                db.session.delete(Account.query.filter_by(UserName = UserName,Password=Password).first())
                db.session.commit()
            except:
                return "Unable to delete account", 400
            return "Account deleted for {}".format(UserName),200
        elif Task == "login":
            AccountSeek = Account.query.filter_by(UserName = UserName,Password=Password).all()
            if len(AccountSeek) == 1:
                return "Login Access Granted"
            elif len(AccountSeek) > 1:
                return "Duplicate account - please delete accounts",400
            else:
                return "Login Access Denied", 400
        else:
            return "Task not correctly specifed - make sure to follow the planning document",400
        
        
    else:
        return "GET request not supported. Use POST requests."

if __name__ == '__main__':
    db.create_all()
    app.run()
