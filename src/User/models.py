'''
Contains user model functions
'''

from flask import jsonify, request, session, redirect, render_template
from passlib.hash import pbkdf2_sha256
from src.app import db, mongodb_client
import uuid



class User:
    '''
    This class handles user session and profile operations 
    '''

    def startSession(self, user):
        '''
        Start the user session
        '''
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        return (jsonify(user), 200)

    def signup(self):
        '''
        User signup using credentials
        '''
        # print(request.form)
        user = {
            '_id': uuid.uuid4().hex,
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'password': request.form.get('password')}
        user['password'] = pbkdf2_sha256.hash(user['password'])
        if db.users.find_one({'email': user['email']}):
            return (jsonify({'error': 'Email address already in use'}),
                    400)

        if db.users.insert_one(user):
            self.startSession(user)
            return redirect('/')



        return (jsonify({'error': 'Signup failed'}), 400)

    def logout(self):
        '''
        Session Logout
        '''
        session.clear()
        return redirect('/')

    def login(self):
        '''
        Session Login
        '''
        user = db.users.find_one({'email': request.form.get('email')})
        if user and pbkdf2_sha256.verify(str(request.form.get('password')), user['password']):
            self.startSession(user)
            return redirect('/')
        return (jsonify({'error': 'Invalid login credentials'}), 401)

    def showProfile(self):
        '''
        Renders User Profile
        '''
        user = session['user']
        return render_template('user_profile.html', user=user)

    def saveResume(self):
        '''
        Saves resume and renders User profile
        '''
        if 'resume_file' in request.files:
            resume = request.files['resume_file']
            mongodb_client.save_file(resume.filename, resume)
            mongodb_client.db.users.insert({'email': request.form.get('email'), 'resume_filename': resume.filename})
        return render_template('user_profile.html')
