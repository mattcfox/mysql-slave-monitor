import pymysql
import requests
import json
from datetime import datetime
import config
from time import sleep

replication_down = False
def check_slave():
    myconn = pymysql.connect(host=config.mysql_host,
                user=config.mysql_user,
                password=config.mysql_pass,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
    try:
        mycurs = myconn.cursor()
        mycurs.execute("SHOW SLAVE STATUS")
        slave_status = mycurs.fetchone()
        
        global replication_down

        if (slave_status["Slave_IO_Running"] == "No" or slave_status["Slave_SQL_Running"] == "No"):
            if not replication_down:
                replication_down = True
                print "{0} - Replication is down".format(str(datetime.now()))
                payload = json.dumps({
                    "text": "Your mysql replication slave has stopped replicating."
                })
                requests.post(config.slack_hook, data = payload)
        else:
            if replication_down:
                print "{0} - Replication is back up".format(str(datetime.now()))
                payload = json.dumps({
                    "text": "Your mysql replication slave is replicating again."
                })
                requests.post(config.slack_hook, data = payload)
            replication_down = False
    except pymysql.Error as e:
        payload = json.dumps({
            "text": "MySQL related error:\n{0}".format(str(e))
        })
        try:
            requests.post(config.slack_hook, data = payload)
        except requests.RequestException as e2:
            print "{0} - Slack Request exception while trying to report MySQL exception:\n{1}".format(str(datetime.datetime.now()), str(e2))
    except requests.RequestException as e:
        print "{0} - Slack Request exception:\n{1}".format(str(datetime.now()), str(e))
    finally:
        myconn.close()

try:
    while True:
        check_slave();
        for i in range(300):
            sleep(1)
except KeyboardInterrupt:
    print "Got Ctl-C shutting down"