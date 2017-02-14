import traceback

try:
    import cx_Oracle
except:
    pass

try:
    import mysql.connector
except:
    pass

try:
    import psycopg2
except:
    pass

DB_ORACLE=0x0
DB_MYSQL=0x1
DB_POSTGRES=0x2

class mysql_database:
    """ mysql connection """
    def __init__(self, username, password, hostname, dbname):
        self.__dbh = None
        self.__cursor = None
        self.__connect(username, password, hostname, dbname)

    def __connect(self, username, password, hostname, dbname):
        self.__dbh = mysql.connector.connect(host=hostname,
                user=username,
                passwd=password,
                db=dbname)
        self.__cursor = self.__dbh.cursor()

    def get_cursor(self):
        return self.__cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cursor.close()
        self.__dbh.close()

class postgres_database:
    """ postgres connection """
    def __init__(self, username, password, hostname, dbname):
        self.__dbh = None
        self.__cursor = None
        self.connect_str = "host='%s' dbname='%s' user='%s' password='%s'" % (hostname, dbname, username, password)
        self.__connect(self.connect_str)

    def __connect(self):
        self.__dbh = psycopg2.connect(self.connect_str)
        self.__cursor = self.__dbh.cursor()

    def get_cursor(self):
        return self.__cursor

class oracle_database:
    """
        handels the database connection
        we assume that all data is read in utf-8, so 
        we can translate it to any encoding... well, that's
        not true, because utf-8 has its limits.
    """
    def __init__(self, username="", password="", sid=""):
        self.__dbh = None
        self.__cursor = None
        self.connect_str = "%s/%s@%s" % (username, password, sid)
        self.__connect()

    def __connect(self):
        self.__dbh = cx_Oracle.connect(self.connect_str)
        self.__cursor = self.__dbh.cursor()

    def get_cursor(self):
        return self.__cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cursor.close()
        self.__dbh.close()

class generic_database:
    """
    generic database interface
    """
    def __init__(self, **args):
        self.DATABASES  = { DB_ORACLE:self.__oracle,DB_MYSQL:self.__mysql,DB_POSTGRES:self.__postgres }
        self.host       = args.pop('host', None)
        self.user       = args.pop('username', None)
        self.passwd     = args.pop('password', None)
        self.dbname     = args.pop('dbname', None)
        self.get_driver = self.DATABASES[args.pop('db_type')]

    def __oracle(self):
        return oracle_database(self.user, self.passwd, self.dbname)

    def __mysql(self):
        return mysql_database(self.user, self.passwd, self.host, self.dbname)

    def __postgres(self):
        return postgres_database(self.user, self.passwd, self.host, self.dbname)

class query_handler:
    """
        returns a normalized data set to a module like csv, json or xml
    """
    def __init__(self, sql_statement=None, db_handler=None):
        self.__db_handler = db_handler
        self.__stmt = sql_statement
        self.__cursor = self.__db_handler.get_cursor()

    def execute_query(self):
        self.__cursor.execute(self.__stmt)

    def get_columns(self):
        return [c[0] for c in self.__cursor.description]

    def get_result(self):
        for row in self.__cursor:
            yield row

    #def get_dict_result(self):
    #    for row in self.__cursor:
    #        yield row

