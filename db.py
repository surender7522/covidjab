from tinydb import TinyDB, Query, where
import json
class DB():
    db=None

    def __init__(self):
        self.db = TinyDB('./db.json')

    def insert_sub(self,table_name,key,value):
        x=self.get_sub(table_name,key)
        print(x)
        if x is not None:
            # update
            y = json.loads(x["value"])
            y.append(value)
            self.remove_key(table_name,key)
            table = self.db.table(table_name)
            table.insert({"key": key, "value": json.dumps(y)})
        else:
            #insert
            table = self.db.table(table_name)
            table.insert({"key": key, "value": json.dumps([value])})


    def get_sub(self,table_name,key):
        table = self.db.table(table_name)
        return table.get(where('key') == key)

    def remove_key(self,table_name, key):
        table = self.db.table(table_name)
        table.remove(where('key') == key)

    def remove_sub(self,table_name, key, value):
        x=self.get_sub(table_name,key)
        print(x)
        if x is not None:
            # update
            y = json.loads(x["value"])
            y.remove(value)
            self.remove_key(table_name,key)
            table = self.db.table(table_name)
            table.insert({"key": key, "value": json.dumps(y)})

    def get_all_sub(self,table_name):
        table = self.db.table(table_name)
        return table.all()

    def insert_usub(self,table_name,key,value):
        x=self.get_usub(table_name,key)
        print(x)
        if x is not None:
            # update
            y = json.loads(x["value"])
            y.append(value)
            self.remove_ukey(table_name,key)
            table = self.db.table(table_name)
            table.insert({"key": key, "value": json.dumps(y)})
        else:
            #insert
            table = self.db.table(table_name)
            table.insert({"key": key, "value": json.dumps([value])})


    def get_usub(self,table_name,key):
        table = self.db.table(table_name)
        return table.get(where('key') == key)

    def remove_ukey(self,table_name, key):
        table = self.db.table(table_name)
        table.remove(where('key') == key)

    def remove_usub(self,table_name, key, value):
        x=self.get_sub(table_name,key)
        print(x)
        if x is not None:
            # update
            y = json.loads(x["value"])
            y.remove(value)
            self.remove_ukey(table_name,key)
            table = self.db.table(table_name)
            table.insert({"key": key, "value": json.dumps(y)})

    def get_all_usub(self,table_name,key):
        table = self.db.table(table_name)
        return table.get(where('key')==key)