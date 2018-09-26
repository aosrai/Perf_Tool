import mysql.connector, os
from mysql.connector import errorcode as errc, connection
import xlsxwriter as xlsx
from xlsxwriter import workbook as wb
from datetime import datetime as dt
from Time_Format import defaultTime, selectedTime


dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

def prepareInfo():
    host_config_file = open(dir + '/Config_File' + '/cnx_host.cfg', 'r')
    line = host_config_file.readline()
    global list_host
    list_host = line.split(' ')
    for host in list_host:
        with open(dir + "/" + 'Config_File/' + host + "_key.txt", 'r') as key_file:
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
                    cursor.execute("SELECT DISTINCT name FROM items WHERE hostid IN (SELECT hostid FROM hosts WHERE host = '{}') AND key_='{}'".format(host,key))
                    global list_name
                    list_name = cursor.fetchall()
                    list_name = [name[0] for name in list_name]
                    for value in list_value:
                        global pairs
                        pairs = {key:value}


def getData():
    from_unixtime = "FROM_UNIXTIME(clock, '%Y/%m/%d %H:%i:%s.%f') AS "
    for host in list_host:
        for key,value in pairs.items():
            table = ['history', 'history_str', 'history_log', 'history_uint', 'history_text']
            cursor = cnx.cursor()
            global itemid
            if user_input == 'd':
                yesterday, present_day = defaultTime()
                cursor.execute("SELECT DISTINCT " + from_unixtime + "clock, a.host, b.name, b.key_, b.itemid, value, b.units "
                                                                        "FROM hosts a, items b, {} c "
                                                                        "WHERE a.host in (SELECT host FROM hosts WHERE host='{}') "
                                                                        "AND b.itemid in(SELECT itemid FROM items WHERE key_='{}') "
                                                                        "AND a.hostid=b.hostid AND b.itemid=c.itemid "
                                                                        "AND clock >= UNIX_TIMESTAMP('{}') AND clock <= UNIX_TIMESTAMP('{}') "
                                                                        "ORDER BY clock ASC".format(table[value], host, key, yesterday, present_day))
                itemid = cursor.fetchall()
            elif user_input == 'u':
                start_time, end_time = selectedTime()
                cursor.execute("SELECT DISTINCT " + from_unixtime + "clock, a.host, b.name, b.key_, b.itemid, value, b.units "
                                                                        "FROM hosts a, items b, {} c "
                                                                        "WHERE a.host in (SELECT host FROM hosts WHERE host='{}') "
                                                                        "AND b.itemid in(SELECT itemid FROM items WHERE key_='{}') "
                                                                        "AND a.hostid=b.hostid AND b.itemid=c.itemid "
                                                                        "AND clock >= UNIX_TIMESTAMP('{}') AND clock <= UNIX_TIMESTAMP('{}') "
                                                                        "ORDER BY clock ASC".format(table[value], host, key, start_time, end_time))
                itemid = cursor.fetchall()

def createReport():
    for host in list_host:
        for key in list_key:
            with xlsx.Workbook(dir + '/Report/' + host + '_Report_' + dt.now().strftime("%Y_%m_%d-%H-%M-%S") + '.xlsx') as wb:
                cell_header_format = wb.add_format({'bold': True, 'align': 'center', 'border': 3})
                cell_format = wb.add_format({'align': 'center', 'border': 3})
                ##########
                head_key, sep, tail_key = key.partition('[')
                ws = wb.add_worksheet(name=head_key)
                ws.set_column(0, 0, 25)
                ws.set_column(1, 1, 15)
                ws.set_column(2, 2, 10)
                ws.write(0, 0, "Clock", cell_header_format)
                ws.write(0, 1, "Host", cell_header_format)
                ws.write(0, 2, "Name", cell_header_format)
                ws.write(0, 3, "Key_", cell_header_format)
                ws.write(0, 4, "ItemID", cell_header_format)
                ws.write(0, 5, "Value", cell_header_format)
                ws.write(0, 6, "Units", cell_header_format)
                ##########
                chartsheet = wb.add_chartsheet(name="Graphs " + head_key)
                chartsheet.set_paper(8)
                chart = wb.add_chart({'type': 'column'})
                for name in list_name:
                    chart.set_title({'name': '{}'.format(name)})
                chart.set_size({'x_scale': 3.2, 'y_scale': 1.2})
                chart.set_x_axis({'num_font': {'bold': False, 'italic': True, 'rotation': -45}, 'name': 'Time'})
                chart.set_y_axis({'num_font': {'bold': False, 'italic': True}, 'name': 'Value'})
                ##########
                for row, line in enumerate(itemid):
                    row = row + 1
                    for col, cell in enumerate(line):
                        ws.write(row, col, cell, cell_format)
                count = 0
                for item in itemid:
                    count = count + 1
                chart.add_series({'categories': ['{}'.format(head_key), 1, 0, count, 0], 'values': ['{}'.format(head_key), 1, 4, count, 4], 'name': '{}'.format(head_key)})
                chartsheet.set_chart(chart)
                print('Created report for host {} done!'.format(host))
            wb.close()

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
        print('Connect successfully!')
        prepareInfo()
        getData()
        createReport()
        print('All done!')
        cnx.close()

if __name__ == '__main__':
    print('What mode do you want to get data? Type d if you want default mode, u for user mode.')
    global user_input
    selection = {'d':'Default mode', 'u':'User mode'}
    user_input = input('Select mode:')
    print('You choose {}'.format(selection[user_input]))
    Connect()
