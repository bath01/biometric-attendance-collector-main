import secrets
import os

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'bornes.sqlite')

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


class Borne(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    adresse_ip = db.Column(db.String(30))
    port = db.Column(db.Integer)
    emplacement = db.Column(db.String(30))
    status = db.Column(db.Boolean(True))
    out_put = db.Column(db.String(50))

    def __init__(self, adresse_ip, port, emplacement, status=True, out_put=""):
        self.adresse_ip = adresse_ip
        self.port = port
        self.emplacement = emplacement
        self.status = status
        self.out_put = out_put


class PostSchema(ma.Schema):
    class Meta:
        fields = ("borne_ip", "port", "emplacement",'status', 'out_put')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)

def init_db():
    db.create_all()

if __name__ == '__main__':
    init_db()
