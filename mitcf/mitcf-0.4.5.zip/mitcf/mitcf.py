import psycopg2

class pglogger(object):

    connection = None

    def connect(self):

            try:
                print('connecting to PostgreSQL database...')
                
                conn_string = "host="+ self.PGHOST +" port="+ self.PGPORT +" dbname="+ self.PGDATABASE +" user=" + self.PGUSER \
                +" password="+ self.PGPASSWORD
                self.connection = psycopg2.connect(conn_string,connect_timeout=3)                
                
                cursor = self.connection.cursor()
                result = cursor.execute('SELECT VERSION()')
                self.connection.commit()
                print cursor.statusmessage                 
                
                data = cursor.fetchone()

            except Exception as error:
                print('Error: connection not established {}'.format(error))

            else:
                print('connection established\n{}'.format(data[0]))

        #return connection

    def __init__(self,creds):
        self.PGHOST = creds.PGHOST  
        self.PGPORT = creds.PGPORT      
        self.PGDATABASE = creds.PGDATABASE      
        self.PGUSER = creds.PGUSER      
        self.PGPASSWORD = creds.PGPASSWORD      
        self.connect()       
        
    def query_insert(self, query):
        try:
            cursor = self.connection.cursor()
            result = cursor.execute(query)
            self.connection.commit()
            print cursor.statusmessage 
            
            #data = cursor.fetchall()
            return 1
        except Exception as error:
            print('error execting query "{}", error: {}'.format(query, error))
            print('trying to reconnect and execute one more time')
            
            try:      
                self.connect()
                    
                cursor = self.connection.cursor()
                result = cursor.execute(query)
                self.connection.commit()
                print cursor.statusmessage 
                    
                #data = cursor.fetchall() 
                return 1
                    
            except Exception as error:
                print('failed to reconnect; give up')
                return 0               

    def query_select(self, query):
        try:
            cursor = self.connection.cursor()
            result = cursor.execute(query)
            self.connection.commit()
            print cursor.statusmessage 
            
            data = cursor.fetchall()
            return data
        except Exception as error:
            print('error execting query "{}", error: {}'.format(query, error))
            return 0   

    def log(self,table,channels,time=0):
        import numpy
        channels_string = numpy.array2string(channels,separator=',')
        channels_string = channels_string[1:-1] # remove brackets
        
        if not time:
            time_string = "NOW() AT TIME ZONE 'America/New_York'"
        else:
        	time_string = "'"+time+"'"

        myquery = "INSERT INTO "+table+" (time,channels) VALUES ("+time_string+",'{"+channels_string+"}')"
        print myquery
        status = self.query_insert(myquery)  
        return status

    def retrieve_last(self,table):
        
        result = self.query_select("SELECT time,channels FROM "+table+" order by time DESC LIMIT 1")
        
        print(result)

        return result 
        
    def close (self): #__del__
        self.connection.close()
        print('connection closed')
        #self.cursor.close()