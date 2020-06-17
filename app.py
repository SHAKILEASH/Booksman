from flask import Flask
import logging as logger
import os

logger.basicConfig(level="DEBUG")
project_dir = os.path.dirname(os.path.abspath(__file__))
Appinstance = Flask(__name__)
Appinstance.config['SECRET_KEY']='11thhour'


if __name__ == '__main__':
    logger.debug("Starting the application")
    from api import *
    Appinstance.run(host="0.0.0.0",port=5000,debug=True,use_reloader=True)
