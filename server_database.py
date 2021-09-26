from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
import json
import urllib.parse
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.sqlite3'
db = SQLAlchemy(app)

class Database(db.Model):
    ID = db.Column(db.Integer, primary_key = True)
    Key_Table = db.Column(db.String(100))
    RawJSONData = db.Column(db.Text())
    def __init__(self,Key_Table, Data):
        self.Key_Table = Key_Table
        self.RawJSONData = Data
    
@app.route('/DB', methods = ["GET","POST"])
def DB():
    if request.method == 'POST':
        Key_Table = None
        Data = None
        Task = None
        DataPairs = request.get_data().decode("utf-8").split("&")
        
        for Pair in DataPairs:
            Pair = Pair.split("=")
            Key = urllib.parse.unquote(Pair[0])
            Value = urllib.parse.unquote(Pair[1])
            if Key == "key":
                Key_Table = Value
            elif Key == "function":
                Task = Value
            elif Key == "data":
                Data = Value
            else:
                return "Malformed JSON input - make sure to follow the planning document",400
        

        if None in [Key_Table,Task]:
            return "Missing key database request data - make sure to follow the planning document",400
        
        if Data != None:
            try:
                json.loads(Data)
            except:
                return "Data not in JSON format", 400
        
        
        if Task == "create":
            KeySeek = Database.query.filter_by(Key_Table=Key_Table).all()
            if len(KeySeek) > 1:
                return "You are trying to create a duplicate table - table creation failed", 400
            
            if Data == None:
                return "No data passed in during table creation - table creation failed", 400
             
            db.session.add(Database(Key_Table,Data))
            db.session.commit()
            return "Table created successfully", 200
        elif Task == "append":
            KeySeek = Database.query.filter_by(Key_Table=Key_Table).all()
            if len(KeySeek) > 1:
                return "You are trying to append to duplicate tables - please delete duplicates - data append failed", 400
            elif len(KeySeek) == 0:
                return "Table not found - data append failed", 400
            NewData = json.loads(Data)
            OldData = json.loads(KeySeek[0].RawJSONData)
            
            for Keys in NewData:
                if Keys in OldData:
                    return "Your old key-value pairs are being overwritten- please change the key names in the new data that you are trying to append", 400
            
            OldData.update(NewData)
            KeySeek[0].RawJSONData = json.dumps(OldData)
            db.session.commit()
            return "Data appended successfully", 200
        elif Task == "view":
            KeySeek = Database.query.filter_by(Key_Table=Key_Table).all()
            if len(KeySeek) > 1:
                return "You are trying to view duplicate tables - please delete duplicates - data viewing failed", 400
            elif len(KeySeek) == 0:
                return "Table not found - data viewing failed", 400
            
            OldData = json.loads(KeySeek[0].RawJSONData)
            Keys =  []
            for Key in OldData:
                Keys.append(Key)
            
            return "{{ keys:'{}' }}".format(Keys), 200
        elif Task == "delete":
            KeySeek = Database.query.filter_by(Key_Table=Key_Table).all()
            if len(KeySeek) > 1:
                return "You are trying to delete duplicate tables - please delete duplicates - data deletion failed", 400
            elif len(KeySeek) == 0:
                return "Table not found - data deletion failed", 400
            
            if Data == None:
                db.session.delete(KeySeek[0])
                db.session.commit()
                return "Deleted all data in {}".format(Key_Table),200
            else:
                OldData = json.loads(KeySeek[0].RawJSONData)
                KeysForDeletion = json.loads(Data)["keys"]
                
                for DataItem in frozenset(OldData):
                    print(DataItem)
                    if DataItem in KeysForDeletion:
                        del OldData[DataItem]
                
                KeySeek[0].RawJSONData = json.dumps(OldData)
                db.session.commit()
                return "Deleted the following keys: {} in {}".format(KeysForDeletion,Key_Table), 200
        elif Task == "get_data":
            KeySeek = Database.query.filter_by(Key_Table=Key_Table).all()
            if len(KeySeek) > 1:
                return "You are trying to get data from duplicate tables - please delete duplicates - data grab failed", 400
            elif len(KeySeek) == 0:
                return "Table not found - data deletion failed", 400
            
            OldData = json.loads(KeySeek[0].RawJSONData)
            DataKey = json.loads(Data)["key"]
            return str(OldData[DataKey]).replace("+"," "), 200
        else:
            return "Task not correctly specifed - make sure to follow the planning document",400
    else:
        return "GET request not supported. Use POST requests."

if __name__ == '__main__':
    db.create_all()
    app.run()
