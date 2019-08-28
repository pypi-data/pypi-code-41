import subprocess
import shlex
import pandas as pd
import json
import sys
import tempfile
import click

@click.command()
@click.option("-f", "--from", "fromDate", help="Date from which to report", default=pd.datetime.now()-pd.Timedelta(days=1))
@click.option("-t", "--to", help="Date up till which to report")
@click.option("-p", "--project", help="Project for which to report")
def watsonReport(fromDate, to, project):
    cmd = "watson log -j "

    if fromDate:
        fromDate = pd.to_datetime(fromDate, dayfirst=True).strftime("%Y-%m-%d")
        cmd += "-f %s " % fromDate
    
    if to:
        toDate = pd.to_datetime(to, dayfirst=True).strftime("%Y-%m-%d")
        cmd += "-t %s "%toDate

    if project:
        cmd += "-p %s" % project
        
    output = json.loads(subprocess.check_output(shlex.split(cmd)))

    df = pd.DataFrame(output)
    if df.empty:
        click.echo("No activities measured since %s"%fromDate)
        return 

    df.start = pd.to_datetime(df.start, utc=True)
    df.stop = pd.to_datetime(df.stop, utc=True)
    df['delta'] = (df.stop - df.start)
    outputfile = tempfile.mktemp(suffix='.xlsx')
    result = df[['project', 'delta']].groupby(['project', df.start.dt.date]).sum().unstack().reset_index().set_index('project').sort_index()
    result.to_excel(outputfile)
    click.echo(result)
    click.echo("%s" % click.format_filename(outputfile))
    click.launch(outputfile)

if __name__ == "__main__":
    watsonReport()
