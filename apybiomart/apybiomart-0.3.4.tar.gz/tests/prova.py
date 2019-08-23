#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Created by Roberto Preste
import timeit


setup_async = """import asyncio
from apybiomart import aquery
loop = asyncio.get_event_loop()
tasks = [aquery(attributes=["ensembl_gene_id", "external_gene_name"],
                    filters={"chromosome_name": str(i)},
                    dataset="hsapiens_gene_ensembl") 
         for i in range(3)]
"""

to_time_async = "dfs = loop.run_until_complete(asyncio.gather(*tasks))"

print(timeit.timeit(to_time_async, setup=setup_async, number=1))

setup_sync = """from pybiomart import Dataset
dataset = Dataset(name='hsapiens_gene_ensembl',
                  host='http://www.ensembl.org')
"""

to_time_sync = """dfs = [dataset.query(attributes=['ensembl_gene_id', 'external_gene_name'], 
filters={'chromosome_name': [str(i)]})
for i in range(3)]"""

print(timeit.timeit(to_time_sync, setup=setup_sync, number=1))
