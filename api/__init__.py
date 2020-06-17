from flask_restful import Api
from .resource import TaskByID,Task
from .resource import User,UserByID,UserLogin
from app import Appinstance
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
import jwt

restServer = Api(Appinstance)

restServer.add_resource(Task,'/api/v1.0/task')
restServer.add_resource(TaskByID,'/api/v1.0/task/id/<string:taskId>')
restServer.add_resource(User,'/api/v1.0/user')
restServer.add_resource(UserByID,'/api/v1.0/user/id/<string:userId>')
restServer.add_resource(UserLogin,'/api/v1.0/login')
