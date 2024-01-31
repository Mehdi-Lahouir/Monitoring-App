import mysql.connector as my

mydb = my.connect(
    user='root',
    password='1234',
    database='db_hosts',
    host='localhost'
)
