from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this'
from app import routes
