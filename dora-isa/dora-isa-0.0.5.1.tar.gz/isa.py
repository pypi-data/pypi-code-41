import re, os
import requests

class ISAContext:
    """
    Contextualiza as consultas a serem executadas
    """
    table_regex = r"""(DESC|DESCRIBE|FROM|JOIN|(?:CREATE TABLE)|(?:CREATE OR REPLACE TABLE)|(?:DROP TABLE))(?:[\s]+)([\d\w\$_]+\.[\d\w\$_]+\.[\d\w\$_]+)(?:(?:[\s])+|\Z|;|\))"""
    table_delta = r"""(DESC|DESCRIBE|FROM|JOIN)(?:[\s]+)([\d\w\$_\.]+)(?:[\s]+)(AsOf\(([0-9]+)\))"""
    endpoint = os.environ.get('MAP_RESOLVER',None)
    
    def __init__(self,spark,debug=False):
        """
        Parameters
        ----------
        spark : object
            recebe o contexto spark
        """
        self.spark = spark
        self.debug = debug

    def get_table(self, alias):
        if self.endpoint is None:
            return alias
        return 'regions'
            
    def query(self, query):
            """
            Executa query usando SparkSQL
            ----------
            query : string
                Recebe a query bruta.
            Returns
            -------
            Dataframe
                retorna o dataframe da query.
            """
            tables = {t[1]:self.get_table(t[1])for t in re.findall(self.table_regex, query, re.MULTILINE | re.IGNORECASE)}
            for key, value in tables.items():
                query=query.replace(key,value)
            if self.debug:
                print(query)
            return self.spark.sql(query)

class ISAMagic:
    from IPython.core.magic import register_cell_magic
    from IPython.core import magic_arguments as magic_arg
    ipython  = get_ipython()
    
    def __init__(self,ISAContext,limit=50):
        self.isa = ISAContext
        self.limit = limit
        self.ipython.register_magic_function(self.sql, 'cell')

    @magic_arg.magic_arguments()
    @magic_arg.argument('connection', nargs='?', default=None)
    def sql(self, line, cell):
        print("limited by {} results".format(self.limit))
        return self.isa.query(cell).limit(self.limit).toPandas()