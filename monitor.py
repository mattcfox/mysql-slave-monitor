import pymysql
import requests
import json
from datetime import datetime

def check_slave():
    myconn = pymysql.connect(host=config["mysql_host"],
                user=config["mysql_user"],
                password=config["mysql_pass"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
    try:
        mycurs = myconn.cursor()
        mycurs.execute("SHOW SLAVE STATUS")
        slave_status = mycurs.fetchone()
    
        if slave_status["Slave_IO_Running"] == "No" or slave_status["Slave_SQL_Running"] == "No"):
            payload = json.dumps({
                "text": "Your mysql replication slave has stopped replicating."
            })
            requests.post(config["slack_hook"], data = payload)
    except pymysql.Error as e:
        payload = json.dumps({
            "text": "MySQL related error:\n{0}".format(str(e))
        })
        try:
            requests.post(config["slack_hook"], data = payload)
        except requests.RequestException as e2:
            print "{0} - Slack Request exception while trying to report MySQL exception:\n{1}".format(str(datetime.datetime.now()).split('.')[0], str(e2))
    except requests.RequestException as e:
        print "{0} - Slack Request exception:\n{1}".format(str(datetime.now()).split('.')[0], str(e))
    finally:
        myconn.close()

try:
    while True:
        check_slave();
        for i in range(300):
            sleep(1)
except KeyboardInterrupt:
    print "Got Ctl-C shutting down"