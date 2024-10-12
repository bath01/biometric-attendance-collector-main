import logging
from datetime import datetime, timedelta
import requests
from zk import ZK as ZK_MANAGER
from models import Borne, app
from const import URL

_logging = logging.getLogger(__file__)


def send_all_datas(datas, output=URL):
    """
     Envoie des donnees de la borne au backend
    """
    url = URL
    headers = {"content-type": "application/json"}
    body = {"params": {"data_list": datas}}
    try:
        result = requests.post(url, json=body, headers=headers)
        _logging.error(str(result.text))
        return result.text
    except Exception as E:
        _logging.error(str(E))


def get_all_datas():
    with app.app_context():
        _logging.error(f"STARTING...{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        all_bornes = Borne.query.all()
        _logging.error(f"all_bornes...{all_bornes}")
        emplacement = {"entree": "entree", "sortie": "sortie"}
        borne_connection = None
        
        for borne in all_bornes:
            _logging.error(f"{borne.emplacement} => {borne.adresse_ip}")
	   
            adresseip = borne.adresse_ip


            _emplacement = emplacement.get(borne.emplacement)

            if not _emplacement: continue

            current_borne_datas = []
            # datas = {"check_in_out": _emplacement}

            zk = ZK_MANAGER(
                borne.adresse_ip,
                port=borne.port,
                timeout=10, password=0,
                force_udp=False,
                ommit_ping=True
            )

            try:
                borne_connection = zk.connect()
                borne_connection.enable_device()
                if borne_connection:
                    attendance = borne_connection.get_attendance()
                    for each in attendance:
                        today = datetime.today().strftime("%Y-%m-%d")
                        #yesterday = (datetime.today() - timedelta(days=3)).strftime("%Y-%m-%d")
                        pointage_date = each.timestamp.strftime("%Y-%m-%d")
           
                        
                        if pointage_date == today:
                            atten_time = each.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                            new_datas = {
                                "check_in_out": _emplacement,
                                "user_id": each.user_id,
                                "pointage_time": atten_time,
                                "atten_time": atten_time,
                                "pointage_heur": each.timestamp.hour + each.timestamp.minute / 60,
                                "pointage_date": pointage_date,
                                "adresse_ip": adresseip
                            }
                            current_borne_datas.append(new_datas)

                    send_all_datas(current_borne_datas, output=borne.out_put)
                    _logging.error(f"{len(current_borne_datas)} Enregistrements envoyes...")
                else:
                    _logging.info(f"Connection Error {borne_connection}")
            except Exception as error:
                _logging.error(str(error))

            finally:
                if borne_connection:
                    try:
                        borne_connection.disconnect()
                    except Exception as error:
                        _logging.error(str(error))
