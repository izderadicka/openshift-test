
import flask
from flask import request, Flask, render_template, make_response
from flask.ext.pymongo import PyMongo  # @UnresolvedImport

import sys
import os
import datetime
from babel.dates import format_timedelta
import pymongo

app = Flask(__name__)
app.config['DEBUG']= os.environ.get('FLASK_DEBUG')


app.config['MONGO_HOST'] = os.environ.get('OPENSHIFT_MONGODB_DB_HOST', 'localhost')
app.config['MONGO_PORT'] = os.environ.get('OPENSHIFT_MONGODB_DB_PORT', 27017)
app.config['MONGO_DBNAME'] = 'testpy'
app.config['MONGO_USERNAME'] = os.environ.get('OPENSHIFT_MONGODB_DB_USERNAME')
app.config['MONGO_PASSWORD'] = os.environ.get('OPENSHIFT_MONGODB_DB_PASSWORD')

mongo=PyMongo(app)

with app.app_context():
    mongo.db.thoughts.ensure_index([('text', pymongo.TEXT)])
    mongo.db.thoughts.ensure_index([('created', pymongo.DESCENDING)])

def format_datetime(value):
    if isinstance(value, datetime.datetime):
        return value.strftime('%d-%b-%Y %H:%M')
    return  value

def format_fromnow(value):
    if isinstance(value, datetime.datetime):
        return format_timedelta(datetime.datetime.now(value.tzinfo)-value, locale='en_US')
    return  value

app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['fromnow'] = format_fromnow

@app.route('/', methods=["GET","POST"])
def root():
    errors=[]
    name=request.cookies.get('name','')
    search=request.args.get('q','')
    if search:
        filter =' '.join(['"'+t+'"' for t in search.split()])
        thoughts=map(lambda r: r['obj'], mongo.db.command('text', 'thoughts', search=filter, limit=100)['results'])
        
    else:
        thoughts=mongo.db.thoughts.find()
        thoughts=thoughts.sort('created', pymongo.DESCENDING).limit(100)
    if request.method=='POST':
        name=request.form['name']
        text=request.form['thought']
        
        if not name:
            errors.append('Name is mandatory')
        if not text:
            errors.append('Thought is mandatory')
        if len(name)>80:
            errors.append('Name is max 80 chars')
        if len(text)>2000:
            errors.append('Though is max 2000 chars')
        if not errors:    
            mongo.db.thoughts.insert({'name':name, 'text':text, 'created':datetime.datetime.utcnow()})
        
    resp = make_response(render_template('index.html', errors='<br>\n'.join(errors), 
                                         thoughts=thoughts, name=name, search=search))  
    if name and request.method=='POST':
        resp.set_cookie('name', name, max_age=315360000)  
    return resp
        
    
    
if __name__ == '__main__':
    app.run()
