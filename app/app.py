from datetime import datetime

from flask import render_template, request
from gunicorn.app.base import BaseApplication
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from models import Borne, app, db
from cron import get_all_datas
from const import JOB_INTERVAL


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/borne_manager", methods=["GET", "POST"])
def borne_manager():
    if request.method == "GET":
        all_post = Borne.query.all()
        return render_template("borne.html", all_post=all_post)

    elif request.method == "POST":
        success, message = False, "Enregistrement effectué"
        borne_id = request.form.get("id")
        borne_ip = request.form.get("borne_ip", "")
        port = request.form.get("port", "4370")
        position = request.form.get("emplacement")
        
        if not borne_ip:
            message = "Veuillez renseigner l'IP de la borne"
        elif not position:
            message = "Veuillez indiqué l'emplacement de la borne"
        else:
            if borne_id:
                current_born = Borne.query.filter_by(_id=borne_id)
                current_born.update({
                    "adresse_ip": borne_ip,
                    "port": port,
                    "emplacement": position,
                })
                success = True
                db.session.commit()
            else:
                port = port or "4370"
                new_borne = Borne(borne_ip, port, position)
                db.session.add(new_borne)
                db.session.commit()
                success = True
        datas = {"success": success, "message": message}
        return datas


@app.route("/delete_borne", methods=["POST"])
def delete_borne():
    borne_id = request.form.get("id")
    borne = Borne.query.get(borne_id)
    db.session.delete(borne)
    db.session.commit()
    datas = {"success": True, "message": "Suppression éffectué"}
    return datas


def start_scheduler():
    scheduler = BackgroundScheduler(
        jobstores={
            'default': SQLAlchemyJobStore(
                url="sqlite:///jobs.sqlite"
            )
        }
    )
    scheduler.start()
    scheduler.add_job(func=get_all_datas, trigger="interval", minutes=JOB_INTERVAL)
    # scheduler.add_job(func=get_all_datas, trigger='date', run_date=datetime(year=2024, month=1, day=1, hour=0, minute=0))


class GunicornApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key, value)

    def load(self):
        return self.application


if __name__ == '__main__':
    # Démarrer le planificateur afin de garantir son execution unique
    start_scheduler()

    gunicorn_options = {
        'bind': '0.0.0.0:5000',
        'workers': 2,
        'preload_app': True,
    }
    GunicornApp(app, gunicorn_options).run()
