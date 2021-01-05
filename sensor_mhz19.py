import mh_z19, time, datetime, logging
import sqlite3 as sl

'''
DB_NAME="co2-data.db"
try:
        con = sl.connect(DB_NAME)
        cursorObj = con.cursor()
        cursorObj.execute("CREATE TABLE co2_info(id integer PRIMARY KEY, timestamp timestamp, SS integer,UhUl integer,TT integer, co2 integer, temperature interger)")
        cursorObj.close()
except Exception as error:
        logging.error("Create table " + str(error))
        cursorObj.close()

while 1:
    data = mh_z19.read_all()
    if data and data["co2"] :
        print(data)
        try:
		sqlite_insert_with_param = """INSERT INTO 'co2_info'
								  ('timestamp','co2','temperature') 
								  VALUES (?, ?,?);"""

		data_tuple = (
			datetime.datetime.now(),  data['co2'], data['temperature'],)
		cursorObj = con.cursor()
		cursorObj.execute(sqlite_insert_with_param, data_tuple)
		con.commit()
		cursorObj.close()

		logging.info("data added successfully \n")
        except Exception as error:
            logging.error("Insert " + str(error))
    time.sleep(600)

con.close()
'''
SAMPLING_ITI = 5
def get_sensor_data():
    
    for t in range(SAMPLING_ITI):
        data = mh_z19.read_all()
        time.sleep(2)
    
    logging.debug("Co2 Data: " + str(data))
    if data and data["co2"] and data["temperature"]:
        return data
    return None

         

