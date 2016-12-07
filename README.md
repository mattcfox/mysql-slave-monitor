# mysql-slave-monitor
A small script to monitor a MySQL replica and report the status to slack
Multi-master replication monitoring is only supported on MariaDB(unless you feel like changing the query)

## Dependencies
* requests
* PyMySQL

## Installation
1. Clone it
2. Copy config.py.template to config.py and fill in the fields
3. You're good to go, `python monitor.py` will start it up
