import mysql.connector #import mysql.connector,os
from mysql.connector import errorcode as errc #from mysql.connector import errorcode as errc, import connection
from mysql.connector import connection
import os
from Time_Perf import SelectedTime

dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") #dòng này là seo ??? 

def GetHostID():
    host_config_file = open(dir + '/Config_File' + '/cnx_host.cfg', 'r') 
    line = host_config_file.readline()
    global list_host
    list_host = line.split(' ')

def GetKey_FromHostID():
    for host in list_host:
        with open(dir + "/" + 'Config_File/' + host + "_key.txt",'r') as key_file:
            line = key_file.readlines()
            for i in line:
                i = i.strip('\n')
                global list_key
                list_key = []
                list_key.append(i)
                for key in list_key:
                    cursor = cnx.cursor()
                    cursor.execute("SELECT value_type FROM items WHERE hostid IN (SELECT hostid FROM hosts WHERE host = '{}') AND key_='{}'".format(host, key))
                    global list_value
                    list_value = cursor.fetchall()
                    list_value = [value[0] for value in list_value]

def GetTableWithTime():
    start_time, end_time = SelectedTime()
    from_unixtime = "FROM_UNIXTIME(clock, '%Y/%m/%d %H:%i:%s.%f') AS "
    table = {0:'history', 1:'history_str', 2:'history_log', 3:'history_uint', 4:'history_text'}
    for host in list_host:
        for key in list_key:
            for value in list_value:
                cursor = cnx.cursor()
                cursor.execute("SELECT DISTINCT " + from_unixtime + "clock, a.host, b.name, b.key_, b.itemid, value, b.units "
                        "FROM hosts a, items b, {} c "
                        "WHERE a.host in (SELECT host FROM hosts WHERE host='{}') "
                        "AND b.itemid in(SELECT itemid FROM items WHERE key_='{}') "
                        "AND a.hostid=b.hostid AND b.itemid=c.itemid "
                        "AND clock >= UNIX_TIMESTAMP('{}') AND clock <= UNIX_TIMESTAMP('{}') "
                        "ORDER BY clock ASC".format(table.get(value), host, key, start_time, end_time))
                itemid = cursor.fetchall()
                print(itemid)

def Connect():
    server_config_file = open(dir + '/Config_File' + '/cnx_server.cfg', 'r')
    line = server_config_file.readline()
    arr = line.split(' ')
    try:
        global cnx
        cnx = connection.MySQLConnection(host=arr[0], user=arr[1], password=arr[2], database=arr[3])
    except mysql.connector.Error as err:
        if err.errno == errc.ER_ACCESS_DENIED_ERROR:
            print('User or password is wrong!')
        elif err.errno == errc.ER_BAD_DB_ERROR:
            print('Database not found.')
        else:
            print(err)
    else:
        print('Connect Successfully!')
        GetHostID()
        GetKey_FromHostID()
        GetTableWithTime()
        print('All done!')
        cnx.close()

Connect()
