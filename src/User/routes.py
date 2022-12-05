'''
These are the end points related to the user
'''


import sys
# sys.path.append('../src')
from src.app import app, mongodb_client
from flask import Flask, render_template, request
from src.User.models import User


@app.route('/user/signup', methods=['POST'])
def signup():
    '''
    User signup
    '''
    return User().signup()


@app.route('/user/logout')
def signout():
    '''
    User signout
    '''
    return User().logout()


@app.route('/user/login', methods=['POST'])
def loginUser():
    '''
    User login
    '''
    return User().login()


@app.route('/user/profile', methods=['GET'])
def showUserProfile():
    '''
    Shows user profile
    '''
    return User().showProfile()


@app.route('/user/saveResume', methods=['POST'])
def saveResume():
    '''
    Saves resume
    '''
    return User().saveResume()


@app.route('/healthcheck', methods=['GET'])
def healthCheck():
    return "Flask is up and running"
