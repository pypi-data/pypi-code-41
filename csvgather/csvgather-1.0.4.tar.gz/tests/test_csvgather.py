import csv
import tempfile
import subprocess

def test_cli() :
    from csvgather import main
    with tempfile.NamedTemporaryFile() as f :
        p = main(
            ['-f','counts',
            '-t','s:counts:{basename}_counts:',
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter='\t')
            assert next(r) == ['ID','sample_A_counts','sample_B_counts','sample_C_counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']

def test_cli_delim() :
    from csvgather import main
    with tempfile.NamedTemporaryFile() as f :
        p = main(
            ['-f','counts',
            '-t','s:counts:{basename}_counts:',
            'tests/sample_A.csv','tests/sample_B.csv','tests/sample_C.csv',
            '-o',f.name,
            '-d',','
            ],
        )
        
        with open(f.name) as f_out :
            r = csv.reader(f_out,delimiter=',')
            assert next(r) == ['ID','sample_A_counts','sample_B_counts','sample_C_counts']
            assert next(r) == ['A' ,'2345'           ,'1119'           ,'881']
