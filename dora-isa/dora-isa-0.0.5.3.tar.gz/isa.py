import re, os,json, datetime
import requests, redis

class ISAContext:
    """
    Contextualiza as consultas a serem executadas
    """
    table_regex = r"""(DESC|DESCRIBE|FROM|JOIN|(?:CREATE TABLE)|(?:CREATE OR REPLACE TABLE)|(?:DROP TABLE))(?:[\s]+)([\d\w\$_]+\.[\d\w\$_]+\.[\d\w\$_]+)(?:(?:[\s])+|\Z|;|\))"""
    table_delta = r"""(DESC|DESCRIBE|FROM|JOIN)(?:[\s]+)([\d\w\$_\.]+)(?:[\s]+)(AsOf\(([0-9]+)\))"""
    
    def __init__(self,spark,metastore='redis:6379',schema='cache',debug=False):
        """
        Parameters
        ----------
        spark : object
            recebe o contexto spark
        metastore : str
            default: 'redis:6379'
            String de conexão com a base redis utilizada como metastore do dora
        schema : str
            default: 'cache'
            Identificador do schema de chache no metastore do dora
        debug : boolean
            quando true ativa o modo debug
        """
        r_host,r_port = metastore.split(':')
        self.spark = spark
        self.debug = debug
        self.cache_schema = schema
        self.redis = redis.Redis(host=r_host, port=r_port)

    def get_table(self, alias):
        alias = alias.upper()
        tbl=self.redis.get(alias)
        if tbl is not None:
            tbl=json.loads(tbl)
            expireUpdate = datetime.datetime.strptime(tbl.get('lastUpdate'), '%Y-%m-%d') + datetime.timedelta(days=int(tbl.get('cacheDays')))
            if expireUpdate > datetime.datetime.now():
                if debug:
                    print("HIT:{}.{}.{}".format(tbl['connection'],tbl['schema'],tbl['table']))
                return "HIVE:{}".format(tbl.get('full_table_name'))
            if debug:
                print("OUTDATED:{}.{}.{}".format(tbl['connection'],tbl['schema'],tbl['table']))
            return "REDIS:{}".format(self.cache_data(meta=tbl))
        if debug:
            print("NEW:{}.{}.{}".format(tbl['connection'],tbl['schema'],tbl['table']))
        return "REDIS:{}".format(self.import_data(alias=alias))
            
    def sql(self, query):
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
                storage,table=value.split(':')
                if storage == 'REDIS':
                    query=query.replace(key,table)
                if storage == 'HIVE':
                    query=query.replace(key,"{}.{}".format(self.cache_schema,table))
                query=query.replace(key,table)
            if self.debug:
                print(query)
            return self.spark.sql(query)
    
    def cache_data(self,meta=None,alias=None):
        if meta is not None:
            temp_view=meta['full_table_name']
            # TODO: Invocar todas as lambdas do Benny para popular o cache no redis
        else:
            temp_view=alias.upper().replace('.','_')
            # TODO: Invocar a função que coleta os metadados da tabela no Swiper
            # TODO: Invocar todas as lambdas do Benny para popular o cache no redis
            # TODO: Registrar essa tabela nos metas do redis
        self.spark.read.format("org.apache.spark.sql.redis").option("table",temp_view).load().createOrReplaceTempView(temp_view)
        return temp_view

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
        return self.isa.sql(cell).limit(self.limit).toPandas()