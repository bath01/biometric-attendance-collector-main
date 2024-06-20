from zk import ZK

adresse_ip = "192.168.1.241"
port = 4370

zk = ZK(
    adresse_ip,
    port=port,
    timeout=10, password=0,
    force_udp=False,
    ommit_ping=True
)

conn = zk.connect()
conn.enable_device()

if conn:
    attendance = conn.get_attendance()
    count = len(attendance)
    for each in attendance:
        pointage_date = each.timestamp.strftime("%Y-%m-%d")
        if pointage_date > "2023-11-22" or pointage_date <= "2023-12-01":
            print(each)
