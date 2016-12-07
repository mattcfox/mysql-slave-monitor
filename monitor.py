import config
import json
from datetime import datetime
from time import sleep
import pymysql
import requests

replication_down = {"default": False}
def check_slave(channel=None):
    myconn = pymysql.connect(host=config.mysql_host,
                             user=config.mysql_user,
                             password=config.mysql_pass,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        mycurs = myconn.cursor()
        if channel:
            mycurs.execute("SHOW SLAVE %s STATUS", [channel])
        else:
            mycurs.execute("SHOW SLAVE STATUS")


        slave_status = mycurs.fetchone()

        global replication_down

        if slave_status["Slave_IO_Running"] == "No" or slave_status["Slave_SQL_Running"] == "No":
            if not replication_down[channel if channel else "default"]:
                replication_down[channel if channel else "default"] = True
                payload = None

                if channel:
                    print "{0} - Replication is down for server \"{1}\" on channel \"{2}\"" \
                        .format(str(datetime.now()), config.server_name, channel)
                    payload = json.dumps({
                        "text": "Your mysql replication slave, \"{0}\", has stopped replicating "
                                "on channel \"{1}\".".format(config.server_name, channel)
                    })
                else:
                    print "{0} - Replication is down for server \"{1}\"" \
                        .format(str(datetime.now()), config.server_name)
                    payload = json.dumps({
                        "text": "Your mysql replication slave, \"{0}\", has stopped replicating."
                                .format(config.server_name)
                    })
                requests.post(config.slack_hook, data=payload)
        else:
            if replication_down[channel if channel else "default"]:
                print "{0} - Replication is back up".format(str(datetime.now()))
                if channel:
                    print "{0} - Replication is back up for server \"{1}\" on channel \"{2}\"" \
                        .format(str(datetime.now()), config.server_name, channel)
                    payload = json.dumps({
                        "text": "Your mysql replication slave, \"{0}\", is replicating again "
                                "on channel \"{1}\".".format(config.server_name, channel)
                    })
                else:
                    print "{0} - Replication is back up for server \"{1}\"" \
                        .format(str(datetime.now()), config.server_name)
                    payload = json.dumps({
                        "text": "Your mysql replication slave, \"{0}\", is replicating again."
                                .format(config.server_name)
                    })
                requests.post(config.slack_hook, data=payload)
            replication_down[channel if channel else "default"] = False
    except pymysql.Error as e:
        payload = json.dumps({
            "text": "MySQL related error:\n{0}".format(str(e))
        })
        try:
            requests.post(config.slack_hook, data=payload)
        except requests.RequestException as e2:
            print "{0} - Slack Request exception while trying to report MySQL exception:\n{1}" \
                .format(str(datetime.now()), str(e2))
    except requests.RequestException as e:
        print "{0} - Slack Request exception:\n{1}".format(str(datetime.now()), str(e))
    finally:
        myconn.close()

try:
    while True:
        try:
            for channel in config.replica_channels:
                check_slave(channel)
        except AttributeError:
            check_slave()

        for i in range(300):
            sleep(1)
except KeyboardInterrupt:
    print "Got Ctl-C shutting down"
