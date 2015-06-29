from setuptools import setup
from setuptools import Command
import os.path

class InitDbCommand(Command):
    user_options = []

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        #init virtualenv
#         virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/' if os.environ.get('OPENSHIFT_PYTHON_DIR') \
#         else os.path.dirname(__file__)
#         virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
#         exec(compile(open(virtualenv, 'rb').read(), virtualenv, 'exec'), dict(__file__=virtualenv)) 
        
        from flaskapp import db
       
        res=db.engine.execute("""
SELECT EXISTS (
   SELECT 1
   FROM   information_schema.tables 
   WHERE  table_schema = 'public'
   AND    table_name = 'thought'
);
""")
        
        exists=list(res)[0][0]
        if exists:
            print('Table already exists, skipping creation')
        else:
            print('Will create table')
            db.create_all() 



setup(name='random_thoughts',
      version='0.1',
      description='Very simple flask app to test Openshift deployment',
      author='Ivan',
      author_email='ivan@zderadicka.eu',
      url='https://testpy-ivanovo.rhcloud.com/',
      cmdclass={'initdb': InitDbCommand},
#      install_requires=['Django>=1.3'],
     )
