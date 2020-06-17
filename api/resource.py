import uuid
from werkzeug.security import generate_password_hash,check_password_hash
import jwt
import datetime
from functools import wraps
from flask_restful import Resource,reqparse
import logging as logger
from app import Appinstance
from flask import jsonify,request
import logging as logger
import os
import json

parser = reqparse.RequestParser()

users ={}
books = {}
DeletedId = []
id = 0



def Iddumper():
  global DeletedId
  for ff in os.listdir():
     if os.path.isfile(ff) and ff == "DeletedId.txt":
         os.remove("DeletedId.txt")
         open("DeletedId.txt","w+").close()
         with open('DeletedId.txt', 'w') as filehandle:
            for listitem in DeletedId:
              filehandle.write('%s\n' % listitem)

def Idloader():
    global DeletedId
    with open('DeletedId.txt', 'r') as filehandle:
      for line in filehandle:
        # remove linebreak which is the last character of the string
         current= line[:-1]
        # add item to the list
         if current != '':
           DeletedId.append(current)
           print("id ::",DeletedId)


def Userdumper():
    global users

    for ff in os.listdir():
       if os.path.isfile(ff) and ff == "User.json":
           os.remove("User.json")
           open("User.json","w+").close()
           with open("User.json","w") as out:
                json.dump(users,out)
                #print("inside dumper",users)

def Bookdumper():
    global books

    for ff in os.listdir():
       if os.path.isfile(ff) and ff == "Books.json":
           os.remove("Books.json")
           open("Books.json","w+").close()
           with open("Books.json","w") as out:
                json.dump(books,out)
                #print("inside dumper",books)

def Userload():
    global users
    with open('User.json', 'r') as f:
         users = json.load(f)
         #print("Json is loaded :",users)

def Bookloader():
    global books
    for ff in os.listdir():
        with open('Books.json', 'r') as f:
           books = json.load(f)
           #print("Json is loaded:",books)

Userload()
Bookloader()
Idloader()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        parser.add_argument('token', type=str)
        values = parser.parse_args()
        #print(values)
        if 'token' in list(values.keys()):
            token = values['token']

        if not token:
            return {'message' : 'Token is missing!'}, 401

        try:
            data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
            #print("\n\n\n\n\n",data['exp'],"\n\n\n")
        except jwt.ExpiredSignatureError:
            return {'message' : 'Token is expired!,Login again '}, 401
        except:
            return {'message' : 'Token is invalid!'}, 401
        return f(*args, **kwargs)

    return decorated


class User(Resource):
    @token_required
    def get(self):
        parser.add_argument('token')
        values = parser.parse_args()
        token = values['token']
        data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
        current_user = users[data['id']]
        #print("\n\n\n",current_user,"\n\n\n")
        if not current_user['admin'] :
            return {"message":"Your not allowed to do this function"},401
        return {"message":"All the users are {}".format(users)},200
    def post(self):
        parser.add_argument('username')
        parser.add_argument('password')
        values = parser.parse_args()
        temp = list(values.values())
        global users
        if values['username']==None:
            return {"message":"please Enter all the details::::"},400
        hashed_password = generate_password_hash(values['password'],method='sha256')
        new_user = { "name":values['username'], "password":hashed_password, "admin":False}
        id = str(uuid.uuid4())
        users[id]=new_user
        Userdumper()
        return {"message":"User created {}".format(id)},200

class UserByID(Resource):
    @token_required
    def get(self,userId):
        parser.add_argument('token')
        values = parser.parse_args()
        token = values['token']
        data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
        current_user = users[data['id']]
        #print("\n\n\n",current_user,"\n\n\n")
        if not current_user['admin'] :
            return {"message":"Your not allowed to do this function"},401
        keys = list(users.keys())
        if userId not in keys:
           return {"message":"No such user"}

        user = users[userId]
        return {"message":"The requested user information {}".format(user)}
    @token_required
    def delete(self,userId):
        global users
        parser.add_argument('token')
        values = parser.parse_args()
        token = values['token']
        data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
        current_user = users[data['id']]
        #print("\n\n\n",current_user,"\n\n\n")
        if not current_user['admin'] :
            return {"message":"Your not allowed to do this function"},401
        keys = list(users.keys())
        if userId not in keys:
           return {"message":"No such user"}

        del(users[userId])
        Userdumper()
        return {"message":"The user is deleted"},200

class UserLogin(Resource):

    def post(self):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        values = parser.parse_args()

        temp = list(users.values())

        if  values['username'] == None:
            return {"message":"please Enter all the details::::"},400

        for user in users:
            #print(users[user]['name'])
            if users[user]['name'] == values['username']:
                if check_password_hash(users[user]['password'],values['password']):
                    token = jwt.encode({'id':user,'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=0.15)},Appinstance.config["SECRET_KEY"])
                    return {'User token': token.decode('UTF-8')},200

        return {'message': 'User not login'},400

class Task(Resource):
    @token_required
    def get(self):
        parser.add_argument('token')
        values = parser.parse_args()
        token = values['token']
        data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
        current_user = users[data['id']]
        #print("\n\n\n",current_user,"\n\n\n")
        if not current_user['admin'] :
            logger.debug("Inside get method")
            userbook =[]
            for book in books:
              if books[book]['user_name'] == current_user['name']:
                 user_book={}
                 user_book['title'] = books[book]['title']
                 user_book['amazon_url'] = books[book]['amazon_url']
                 user_book['author'] = books[book]['author']
                 user_book['genre'] = books[book]['genre']
                 user_book['user_name'] = books[book]['user_name']
                 userbook.append(user_book)
            return {"message":"Your books are {}".format(userbook)},200

        return {"message":"List of books {}".format(books)},200
    @token_required
    def post(self):
        global books
        global users
        global DeletedId

        #print(users,"\n\n\n")
        parser.add_argument('token')
        values = parser.parse_args()
        token = values['token']
        data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
        current_user = users[data['id']]

        logger.debug("Inside the post method of TaskById")
        parser.add_argument('title', type=str)
        parser.add_argument('amazon_url', type=str)
        parser.add_argument('author', type=str)
        parser.add_argument('genre', type=str)
        values = parser.parse_args()
        #print(values)
        temp = list(values.values())
        if values['title'] == None:
            return {"message":"please Enter all the details::::"},400
        if len(DeletedId)==0:
         print(list(books.keys()))
         id = int(list(books.keys())[-1])

         id+=1
         id = str(id)
         temp = [int(i) for i in list(books.keys())]
         if id in list(books.keys()):
             id = max(temp)+1
             id = str(id)

        else:
          id = DeletedId[-1]
          DeletedId.pop()
          Iddumper()

        books[id] = {'title':values['title'],'amazon_url':values['amazon_url'],'author':values['author'],'genre':values['genre'],"user_name":current_user['name']}
        #print(books)
        Bookdumper()

        return {"message" : "Inside post method of TaskByID. TaskId : {} ".format(id)},200


class TaskByID(Resource):

    @token_required
    def get(self,taskId):
        parser.add_argument('token')
        values = parser.parse_args()
        token = values['token']
        data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
        current_user = users[data['id']]
        logger.debug("Inisde the get method of TaskById. TaskID = {}".format(taskId))
        key = list(books.keys())
        if taskId not in key:
            return {"message":"No such key"}
        value = books[taskId]
        username = value['user_name']
        if username is current_user['name']:
         title = value["title"]
         return {"message" : "Inside get method of TaskByID. TaskByID = {} title = {}".format(taskId,title)},200
        else:
            return {"message":"The requested book Cannot be viewed"},401

    @token_required
    def put(self,taskId):
        global books
        parser.add_argument('token')
        values = parser.parse_args()
        token = values['token']
        data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
        current_user = users[data['id']]
        logger.debug("Inisde the put method of TaskByID. TaskID = {}".format(taskId))
        key = list(books.keys())
        if taskId not in key:
            return {"message":"No such key"}
        parser.add_argument('title', type=str)
        parser.add_argument('amazon_url', type=str)
        parser.add_argument('author', type=str)
        parser.add_argument('genre', type=str)
        values = parser.parse_args()
        value = books[taskId]
        print(value)
        username = value['user_name']
        print("names",username,current_user['name'])
        if username == current_user['name']:
          if values["title"] != None:
            books[taskId]={"title":values["title"],'amazon_url':books[taskId]['amazon_url'],'author':books[taskId]['author'],'genre':books[taskId]['genre'],"user_name":books[taskId]['user_name']}
          if values["amazon_url"] != None:
            books[taskId]={"title":books[taskId]["title"],'amazon_url':values['amazon_url'],'author':books[taskId]['author'],'genre':books[taskId]['genre'],"user_name":books[taskId]['user_name']}
          if values["author"] != None:
            books[taskId]={"title":books[taskId]["title"],'amazon_url':books[taskId]['amazon_url'],'author':values['author'],'genre':books[taskId]['genre'],"user_name":books[taskId]['user_name']}
          if values["genre"] != None:
            books[taskId]={"title":books[taskId]["title"],'amazon_url':books[taskId]['amazon_url'],'author':books[taskId]['author'],'genre':values['genre'],"user_name":books[taskId]['user_name']}
          Bookdumper()
          return {"message" : "Inside put method of TaskById. TaskID = {}".format(books[taskId])},200
        else:
         return {"message":"Your not allowed to update this book"}

    @token_required
    def delete(self,taskId):
        global books
        global DeletedId

        parser.add_argument('token')
        values = parser.parse_args()
        token = values['token']
        data = jwt.decode(token, Appinstance.config['SECRET_KEY'])
        current_user = users[data['id']]
        logger.debug("Inisde the delete method of TaskByID. TaskID = {}".format(taskId))
        key = list(books.keys())
        if taskId not in key:
            return {"message":"No such key"}
        value = books[taskId]

        username = value['user_name']
        if username == current_user['name']:
          del(books[taskId])
          DeletedId.append(taskId)
          print(DeletedId)
          Iddumper()
          Bookdumper()
          return {"message" : "Deleted:{}".format(taskId)},200
        else:
           return {"message":"Your not allowed to delete this Book."}
