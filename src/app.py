from functools import wraps

"""
The module app holds the function related to flask app and database.
"""
"""Copyright 2022 Tejas Prabhu

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

from flask import Flask, render_template, request, session, redirect  # noqa: E402
from flask_pymongo import PyMongo  # noqa: E402
from pandas import DataFrame  # noqa: E402
import re  # noqa: E402
import numpy as np  # noqa: E402

app = Flask(__name__)

app.secret_key = b'\xe1\x04B6\x89\xf7\xa0\xab\xd1L\x0e\xfb\x1c\x08"\xf6'
# client = pymongo.MongoClient('localhost', 27017)
# db = client.user_system


mongo_conn = "mongodb+srv://subodh:se2022@cluster0.fcrvo9n.mongodb.net/job_analyzer"
mongo_params = "?tlsAllowInvalidCertificates=true&retryWrites=true&w=majority"
app.config["MONGO_URI"] = mongo_conn + mongo_params

mongodb_client = PyMongo(app)
db = mongodb_client.db


def login_required(f):

    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap


@app.route('/signup')
def sgup():
    """
    Route: '/'
    The index function renders the index.html page.
    """
    return render_template('signup.html')


@app.route('/login')
def lgin():
    """
    Route: '/'
    The login function renders login.html page.
    """
    return render_template('login.html')


@app.route('/')
def index():
    """
    Route: '/'
    The index function renders the index.html page.
    """
    return render_template('index.html')


@app.route('/login')
def login():
    """
    Route: '/login'
    The index function renders the login.html page.
    """
    return render_template('login.html')


@app.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    print(request)
    """
    Route: '/search'
    The search function renders the get_job_postings.html.
    Upon submission fetches the job postings from the database and renders job_posting.html
    """
    if request.method == 'POST':
        print("into req post")
        print(db.get_collection)
        job_df = read_from_db(request, db)
        job_count = job_df.shape[0]
        print(job_count)
        if job_df.empty:
            job_count = 0
            return render_template('no_jobs.html', job_count=job_count)
        job_df = job_df.drop('Job Description', axis=1)
        job_df = job_df.drop('_id', axis=1)
        job_df = job_df.drop('Industries', axis=1)
        job_df = job_df.drop('Job function', axis=1)
        job_df = job_df.drop('Total Applicants', axis=1)
        job_df['Job Link'] = '<a href=' + job_df['Job Link'] + '><div>' + " Apply " + '</div></a>'
        job_link = job_df.pop("Job Link")
        job_df.insert(7, "Job Link", job_link)
        job_df['Job Link'] = job_df['Job Link'].fillna('----')
        return render_template('job_posting.html', job_count=job_count,
                               tables=['''
    <style>
        .table-class {border-collapse: collapse;    margin: 24px 0;    font-size: 1em;
        font-family: sans-serif;    min-width: 500px;    box-shadow: 0 0 19px rgba(0, 0, 0, 0.16);}
        .table-class thead tr {background-color: #009878;    color: #ffffff;    text-align: left;}
        .table-class th,.table-class td {    text-align:center; padding: 12.4px 15.2px;}
        .table-class tbody tr {border-bottom: 1.1px solid #dddddd;}
        .table-class tbody tr:nth-of-type(even) {    background-color: #f3f3f3;}
        .table-class tbody tr:last-of-type {    border-bottom: 2.1px solid #009878;}
        .table-class tbody tr.active-row {  font-weight: bold;    color: #009878;}
        table tr th { text-align:center; }
    </style>
    ''' + job_df.to_html(classes="table-class", render_links=True, escape=False)],
            titles=job_df.columns.values)
    return render_template('get_job_postings.html')


def add(db, job_data):
    """
    The add function adds the skills column and adds the job data to the database.
    """
    job_data['skills'] = [','.join(map(str, skill)) for skill in job_data['skills']]
    job_data['skills'] = job_data['skills'].replace(r'^\s*$', np.nan, regex=True)
    job_data['skills'] = job_data['skills'].fillna('----')
    db.jobs.insert_many(job_data.to_dict('records'))


def read_from_db(request, db):
    """
    The read_from_db function reads the job details based on the input provided using regex.
    Returns a DataFrame with the details
    """
    job_title = request.form['title']
    job_location = request.form['location']
    company_name = request.form['companyName']
    skills = request.form['skills']
    regex_char = ['.', '+', '*', '?', '^', '$', '(', ')', '[', ']', '{', '}', '|']

    for char in regex_char:
        skills = skills.replace(char, '\\'+char)

    rgx_title = re.compile('.*' + job_title + '.*', re.IGNORECASE)
    rgx_location = re.compile('.*' + job_location + '.*', re.IGNORECASE)
    rgx_company_name = re.compile('.*' + company_name + '.*', re.IGNORECASE)
    rgx_skills = re.compile('.*' + skills + '.*', re.IGNORECASE)

    data_filter = {}
    if job_title != '':
        data_filter['Job Title'] = rgx_title
    if job_location != '':
        data_filter['Location'] = rgx_location
    if company_name != '':
        data_filter['Company Name'] = rgx_company_name
    if skills != '':
        data_filter['skills'] = rgx_skills

    data = db.jobs.find(data_filter)
    return DataFrame(list(data))
