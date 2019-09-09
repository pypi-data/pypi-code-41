'''
Usage: csvgather.py [options] [-j PATT]... [-f PATT]... [-t STR]... <csv_fn>...

Options:
  -h --help               This helpful help help help help is a weird word
  -d STR --delimiter=STR  Character(s) to use as the delimiter in the output,
                          can be multiple characters [default: \t]
  -o PATH --output=PATH   Output to file [default: stdout]
  -j COL --join=COL       Column(s) to join on. Can take one of four forms:
                            - 0-based integer indicating column index, can be
                              negative to index from the end of the columns
                            - a half closed interval of 0-based integers to
                              specify a range of columns (e.g. 0:4 or 0:-1)
                            - a regular expression that will use any columns it
                              matches as the join columns
                            - a pair of regular expressions to specify a range
                              of columns (e.g. geneName:strand will start with
                              the column geneName and end with column strand)
                          If more than one column matches, then a warning is
                          issued but the join continues on the aggregate of the
                          columns. ':' or special regular expression characters
                          (e.g. +, *, [, ], etc) in column names must be
                          wrapped in [], e.g. '[:]'. Can be specified multiple
                          times, in which case all selected columns are unioned
                          together [default: 0]
  -f COL --field=COL      Column(s) to select fields for concatenation. Uses
                          the same format as -j option. May be specified
                          multiple times and any matching columns will be
                          included. Column selection occurs before application
                          of transformations (-t). Joined columns are not
                          included in the field match [default: .]
  -t STR --transform=STR  A string of the form "s:patt:repl:[gi]" to apply to
                          every column name. The special strings {path}, {dir},
                          {fn}, and {basename} can be used in the repl string to
                          refer to the full path, parent directory name, file
                          name, and filename without extension (i.e. [.][^.]*$)
                          removed. repl may be empty. If specified more than
                          once, each subsequent transform will be applied to
                          the previously transformed sample names in the order
                          provided on the command line [default: s:.:.:]
  --join-type=STR         Type of join, one of 'outer', 'inner', or 'left'.
                          outer will create a row for every distinct value in
                          the -j column(s), inner will report only rows that
                          are found in all files, and left will join files from
                          left to right [default: outer]
  --empty-val=VAL         The value to use when an outer or left join does not
                          find a corresponding row in a file [default: ]
  --comment=CHARS         Characters to be considered comments in input files
                          and will be skipped. Can be any number of characters
                          e.g. #@- [default: #]
'''

#TODO
'''
  --strict                Fail on any of the following:
                            - specified join columns do not exist in all files
                            - -j or -f columns do not match any fields in any
                              single file
                            - -t does not apply to any columns
'''

import csv
from docopt import docopt, DocoptExit
import os
import pandas
import re
import sys
import warnings

# ignore pandas parsing warnings since we are sniffing on our own
warnings.filterwarnings(action='ignore',message='Conflicting values for')

def unique(l) :
    '''Return only unique elements of l in place'''
    if not l :
        return []
    else :
        if l[-1] in l[:-1] :
            return unique(l[:-1])
        else :
            return unique(l[:-1])+[l[-1]]

index_re = re.compile('(?P<start>[-]?\d+)(:(?P<end>[-]?\d+))?')
regex_re = re.compile(     '(?P<start>[^:]*(\[:\])?[^:]+)'
                                             '(:(?P<end>.*(\[:\])?.+))?')
def parse_spec(spec) :

    if index_re.match(spec) :
         m = index_re.match(spec)
         col_start = int(m.group('start'))
         col_end = m.group('end')
         col_end = int(col_end) if col_end is not None else col_end
    elif regex_re.match(spec) :
         m = regex_re.match(spec)
         col_start = re.compile(m.group('start'))
         col_end = m.group('end')
         col_end = re.compile(col_end) if col_end is not None else col_end
    else :
        raise Exception('Could not understand column spec: {}'.format(spec))

    return col_start, col_end

def filter_columns(cols,spec) :
    filt_cols = []
    for col_st, col_en in spec :
        if isinstance(col_st,int) : # indices
            if col_en is not None :
                filt_cols.extend(cols[col_st:col_en])
            else :
                filt_cols.append(cols[col_st])
        else : # regex
            if col_en is not None :
                st_matches = [cols.index(_) for _ in cols if col_st.search(_)]
                en_matches = [cols.index(_) for _ in cols if col_en.search(_)]
                filt_cols.extend(cols[min(st_matches):max(en_matches)+1])
            else :
                st_matches = [_ for _ in cols if col_st.search(_)]
                filt_cols.extend(st_matches)

    filt_cols = unique(filt_cols)

    return filt_cols

def main(args=sys.argv[1:]) :

    args = docopt(__doc__,argv=args)

    # validate args
    join_col_spec = []
    for join_spec in args['--join'] :
         try:
             join_col_spec.append(parse_spec(join_spec))
         except Exception as e:
                raise DocoptExit('--join: '+e.msg)

    field_col_spec = []
    for field_spec in args['--field'] :
         try:
             field_col_spec.append(parse_spec(field_spec))
         except Exception as e:
                raise DocoptExit('--field: '+e.msg)

    # transform
    transforms = []
    transf_re = re.compile('^s:(?P<patt>[^:]*(\[[:*+[]|]\])?[^:]+)+'
                                                     ':(?P<repl>[^:]*(\[[:*+[]|]\])?[^:]+)*'
                                                     ':(?P<mode>g?i?)$')
    for transf_spec in args['--transform'] :
        m = transf_re.match(transf_spec)
        if m :
            transforms.append((m.group('patt'),m.group('repl'),m.group('mode')))
        else :
            raise DocoptExit('Could not understand the transformation spec: {}'.format(transf_spec))

    # join type
    if args['--join-type'] not in ('outer','inner','left') :
        raise DocoptExit('--join-type must be one of outer, inner, or left')

    merged = None

    for fn in args['<csv_fn>'] :
        with open(fn,'rt') as f :
          # sniffing formats in the presence of comments is really hard
          # apparently, scan to the middle of the file for a sample
          lines = []
          for l in f :
            if l[0] not in args['--comment'] :
              lines.append(l)
            if len(lines) == 1000 :
              break
          if len(lines) == 0 :
            warnings.warn('{} had no non-comment lines, skipping'.format(fn))
            continue
          sniff = csv.Sniffer().sniff(''.join(lines),delimiters=',\t')
          f.seek(0)
          df = pandas.read_csv(f,dialect=sniff,comment='#') 

        # select join columns
        join_cols = filter_columns(df.columns.tolist(),join_col_spec)
        if len(join_cols) == 0 :
            sys.exit('No join columns were selected, aborting')

        df.index = df[join_cols]
        df.drop(columns=join_cols,inplace=True)

        # selected fields
        select_cols = filter_columns(df.columns.tolist(),field_col_spec)
        df = df[select_cols]

        # transform fields
        fn_dir, fn_base = os.path.split(fn)
        fn_basename, fn_ext = os.path.splitext(fn_base)
        for patt, repl, mode in transforms :
            count = 0 if 'g' in mode else 1
            flag = re.I if 'i' in mode else 0
            if repl is None : # repl was empty
              repl = ''
            else:
              repl = repl.replace('{path}',fn)
              repl = repl.replace('{dir}',fn_dir)
              repl = repl.replace('{fn}',fn_base)
              repl = repl.replace('{basename}',fn_basename)
              repl = repl.replace('&','\g<0>')

            for colname in select_cols :
                df.rename(
                    columns={colname:re.sub(patt,repl,colname,count,flag)},
                    inplace=True
                )

            select_cols = df.columns

        if merged is None :
          merged = df
        else :
          merged = pandas.merge(merged,df,
                  how=args['--join-type'],
                  left_index=True,
                  right_index=True
          )

    merged.fillna(args['--empty-val'],inplace=True)

    out_f = sys.stdout if args['--output'] == 'stdout' else open(args['--output'],'wt')

    out_csv = csv.writer(out_f,delimiter=args['--delimiter'])
    out_csv.writerow(join_cols+merged.columns.tolist())
    for k, row in merged.iterrows() :
      out_csv.writerow(list(k)+row.tolist())

if __name__ == '__main__' :


    main()
