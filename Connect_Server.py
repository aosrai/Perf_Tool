import mysql.connector, os
from mysql.connector import errorcode as errc, connection
import xlsxwriter as xlsx
from xlsxwriter import workbook as wb
from datetime import datetime as dt
from Time_Format import defaultTime, selectedTime
from Para_Format import action

dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

def prepareInfo():
    host_config_file = open(dir + '/Config_File' + '/cnx_host.cfg', 'r')
    list_host = host_config_file.readlines()
    list_host = [i.replace('\n', '') for i in list_host]
    for host in list_host:
        with xlsx.Workbook(dir + '/Report/' + host + '_Report_' + dt.now().strftime("%Y_%m_%d-%H-%M-%S") + '.xlsx') as wb:
            with open(dir + "/" + 'Config_File/' + host + "_key.txt", 'r') as key_file:
                list_key = key_file.readlines()
                list_key = [i.replace('\n', '') for i in list_key]
                for key in list_key:
                    cursor = cnx.cursor()
                    #Create value list
                    cursor.execute("SELECT value_type FROM items WHERE hostid IN (SELECT hostid FROM hosts WHERE host = '{}') AND key_='{}'".format(host, key))
                    list_value = cursor.fetchall()
                    list_value = [value[0] for value in list_value]
                    #Create name list
                    cursor.execute("SELECT DISTINCT name FROM items WHERE hostid IN (SELECT hostid FROM hosts WHERE host = '{}') AND key_='{}'".format(host, key))
                    list_name = cursor.fetchall()
                    list_name = [name[0] for name in list_name]

                    #Get data
                    from_unixtime = "FROM_UNIXTIME(clock, '%Y/%m/%d %H:%i:%s.%f') AS "
                    table = ['history', 'history_str', 'history_log', 'history_uint', 'history_text']
                    ##Default mode
                    if action == 'default':
                        yesterday, present_day = defaultTime()
                        for value in list_value:
                            cursor = cnx.cursor()
                            cursor.execute("SELECT DISTINCT " + from_unixtime + "clock, a.host, b.name, b.key_, b.itemid, value, b.units "
                                                                            "FROM hosts a, items b, {} c "
                                                                            "WHERE a.host in (SELECT host FROM hosts WHERE host='{}') "
                                                                            "AND b.itemid in(SELECT itemid FROM items WHERE key_='{}') "
                                                                            "AND a.hostid=b.hostid AND b.itemid=c.itemid "
                                                                            "AND clock >= UNIX_TIMESTAMP('{}') AND clock <= UNIX_TIMESTAMP('{}') "
                                                                            "ORDER BY clock ASC".format(table[value], host, key, yesterday, present_day))
                            itemid = cursor.fetchall()
                        ##User mode
                    elif action == 'user':
                        startTime, endTime = selectedTime()
                        for value in list_value:
                            cursor = cnx.cursor()
                            cursor.execute("SELECT DISTINCT " + from_unixtime + "clock, a.host, b.name, b.key_, b.itemid, value, b.units "
                                                                            "FROM hosts a, items b, {} c "
                                                                            "WHERE a.host in (SELECT host FROM hosts WHERE host='{}') "
                                                                            "AND b.itemid in(SELECT itemid FROM items WHERE key_='{}') "
                                                                            "AND a.hostid=b.hostid AND b.itemid=c.itemid "
                                                                            "AND clock >= UNIX_TIMESTAMP('{}') AND clock <= UNIX_TIMESTAMP('{}') "
                                                                            "ORDER BY clock ASC".format(table[value], host, key, startTime, endTime))
                            itemid = cursor.fetchall()

                    #Create report
                    cell_header_format = wb.add_format({'bold': True, 'align': 'center', 'border': 3})
                    cell_format = wb.add_format({'align': 'center', 'border': 3})
                    #Format for data sheet#
                    head_key, sep, tail_key = key.partition('[')
                    for name in list_name:
                        ws = wb.add_worksheet(name=name)
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
                    #Format for chart sheet#
                    for name in list_name:
                        chartsheet = wb.add_chartsheet(name= 'G' + name)
                    chartsheet.set_paper(8)
                    chart = wb.add_chart({'type': 'column'})
                    for name in list_name:
                        chart.set_title({'name': '{}'.format(name)})
                    chart.set_size({'x_scale': 3.2, 'y_scale': 1.2})
                    chart.set_x_axis({'num_font': {'bold': False, 'italic': True, 'rotation': -45}, 'name': 'Time'})
                    chart.set_y_axis({'num_font': {'bold': False, 'italic': True}, 'name': 'Value'})
                    #Write data to data sheet#
                    for row, line in enumerate(itemid):
                        row = row + 1
                        for col, cell in enumerate(line):
                            ws.write(row, col, cell, cell_format)
                    #Draw chart sheet#
                    count = 0
                    for item in itemid:
                        count = count + 1
                    for name in list_name:
                        chart.add_series({'categories': ['{}'.format(name), 1, 0, count, 0], 'values': ['{}'.format(name), 1, 5, count, 5], 'name': '{}'.format(head_key)})
                    chartsheet.set_chart(chart)
                print('Created report for host {} done!'.format(host))
                wb.close()

def connectServer():
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
        print('Done.')
        cnx.close()

if __name__ == '__main__':
    connectServer()




