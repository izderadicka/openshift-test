
import flask
from flask import request, Flask, render_template, make_response
from flask.ext.sqlalchemy import SQLAlchemy

import sys
import os
import datetime
from babel.dates import format_timedelta

app = Flask(__name__)
app.config['DEBUG']= os.environ.get('FLASK_DEBUG')


db_host=os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST', 'localhost')
db_port=int(os.environ.get('OPENSHIFT_POSTGRESQL_DB_PORT', 5432))
db_user=os.environ.get('OPENSHIFT_POSTGRESQL_DB_USERNAME', 'ivan')
db_pwd=os.environ.get('OPENSHIFT_POSTGRESQL_DB_PASSWORD', '')
db_db=os.environ.get('PGDATABASE', 'testbase')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@%s:%d/%s' %(db_user, db_pwd,db_host,db_port,db_db)

db=SQLAlchemy(app)

class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), index=True)
    text = db.Column(db.String(1000))
    created = db.Column(db.DateTime, index=True, default=lambda: datetime.datetime.now())
    

def format_datetime(value):
    if isinstance(value, datetime.datetime):
        return value.strftime('%d-%b-%Y %H:%M')
    return  value

def format_fromnow(value):
    if isinstance(value, datetime.datetime):
        return format_timedelta(datetime.datetime.now()-value, locale='en_US')
    return  value

app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['fromnow'] = format_fromnow

@app.route('/', methods=["GET","POST"])
def root():
    errors=[]
    name=request.cookies.get('name','')
    search=request.args.get('q')
    if search:
        filter=[Thought.text.ilike('%'+t+'%') for t in search.split()]
        thoughts=Thought.query.filter(*filter)
    else:
        thoughts=Thought.query
    thoughts=thoughts.order_by(Thought.created.desc()).limit(100)
    if request.method=='POST':
        name=request.form['name']
        text=request.form['thought']
        
        if not name:
            errors.append('Name is mandatory')
        if not text:
            errors.append('Thought is mandatory')
        if not errors:    
            t=Thought(name=name,text=text)
            db.session.add(t)
            db.session.commit()
        
    resp = make_response(render_template('index.html', errors='<br>\n'.join(errors), 
                                         thoughts=thoughts, name=name))  
    if name and request.method=='POST':
        resp.set_cookie('name', name, max_age=315360000)  
    return resp
        
    
    
if __name__ == '__main__':
    app.run()
