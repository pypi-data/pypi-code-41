import pandas as pd
from interop import py_interop_run_metrics, py_interop_run, py_interop_summary
from tabulate import tabulate


class SummaryStat(object):
    def __init__(self, input_folder):
        self.run_folder = input_folder  #
        # run_folder = '/data/users/pmrefael/workspace/illumina-interop/InterOp-example'
        # # run_folder = '/data/users/pmrefael/workspace/illumina-interop/MiSeqDemo'

    def upload_interop_files(self):
        run_folder = self.run_folder
        run_metrics = py_interop_run_metrics.run_metrics()
        valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
        py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)
        run_metrics.read(run_folder, valid_to_load)
        run_metrics.read_run_info(run_folder)
        summary = py_interop_summary.run_summary()
        py_interop_summary.summarize_run_metrics(run_metrics, summary)
        return summary, run_metrics

    def get_total_stat(self, summary):
        columns = (
            ('Yield Total (G)', 'yield_g'), ('Projected Yield (G)', 'projected_yield_g'),
            ('% Aligned', 'percent_aligned'), ('% > Q30', 'percent_gt_q30'), ('Error rate', 'error_rate'),
            ('First cycle intensity', 'first_cycle_intensity'))
        rows_total = [('Non-Indexed Total', summary.nonindex_summary()), ('Total', summary.total_summary())]
        rows_reads = [("Read %s%d" % ("(I)" if summary.at(i).read().is_index() else " ", summary.at(i).read().number()),
                       summary.at(i).summary()) for i in xrange(summary.size())]
        rows = rows_total + rows_reads
        d = []
        for label, func in columns:
            d.append((label, pd.Series([getattr(r[1], func)() for r in rows], index=[r[0] for r in rows])))
        df = pd.DataFrame.from_items(d)
        return df

    def format_value(self, val):
        if hasattr(val, 'mean'):
            return val.mean()
        else:
            return val

    """
        percent_gt_q30
        yield_g
        projected_yield_g
        reads
        reads_pf
        density
        density_pf
        cluster_count
        cluster_count_pf
        percent_pf
        phasing
        prephasing
        percent_aligned
        error_rate
        error_rate_35
        error_rate_50
        error_rate_75
        error_rate_100
        first_cycle_intensity
        phasing_slope
        phasing_offset
        prephasing_slope
        prephasing_offset
    """

    def get_per_read_stat(self, summary, read):
        columns = (('Lane', 'lane'), ('Density (1/mm2)', 'density'), ('Cluster PF (%)', 'percent_pf'),
                   ('Reads', 'reads'), ('Reads PF', 'reads_pf'), ('% > Q30', 'percent_gt_q30'),
                   ('Yield Total (G)', 'yield_g'), ('% Aligned', 'percent_aligned'), ('Error rate', 'error_rate'))
        rows = [summary.at(read).at(lane) for lane in xrange(summary.lane_count())]
        d = []
        for label, func in columns:
            if func == 'reads' or func == 'reads_pf':
                d.append((label + ' (M)', pd.Series([self.format_value(getattr(r, func)()) / 1000000 for r in rows])))
            elif func == 'density':
                d.append(('Density (K/mm2)', pd.Series([self.format_value(getattr(r, func)()) / 1000 for r in rows])))
            else:
                d.append((label, pd.Series([self.format_value(getattr(r, func)()) for r in rows])))
        df = pd.DataFrame.from_items(d)
        return df

    @staticmethod
    def write_stats(input_foler, output_file):
        # mail = "From: bioinfo@weizmann.ac.il\nTo: refael.kohen@weizmann.ac.il\nSubject: A simple example\nContent-Type: text/html; charset=UTF-8\n\n"
        summary_stat = SummaryStat(input_foler)
        # summary cannot be part of SummaryStat object
        summary, run_metrics = summary_stat.upload_interop_files()
        total_df = summary_stat.get_total_stat(summary)

        # print run_metrics.run_info().useable_cycles() #http://illumina.github.io/interop/group__run__info.html#ga5d1372ff32185e7d8a64acb38c65bcf5
        # print run_metrics.run_info().reads()[0].last_cycle() #http://illumina.github.io/interop/group__cycle__range.html

        with open(output_file, 'w') as fh:
            #        with PDF(output_file) as fh:
            # fh.write(mail)

            fh.write('Flowcell: %s\n\n' % run_metrics.run_info().name())
            fh.write('Reads number: %s\n\n' % len(run_metrics.run_info().reads()))
            prev_last_cycle = 0
            for read in xrange(len(run_metrics.run_info().reads())):
                last_cycle = run_metrics.run_info().reads()[read].last_cycle()
                num_cycles = last_cycle - prev_last_cycle
                prev_last_cycle = last_cycle
                fh.write('Cycles in read %s: %s\n\n' % (read + 1, num_cycles))
            fh.write('\n')
            fh.write(tabulate(total_df, headers='keys', showindex=True, tablefmt='testile'))
            for read in xrange(summary.size()):
                fh.write('\n\nRead %s:' % str(read + 1) + '\n\n')
                read_df = summary_stat.get_per_read_stat(summary, read)
                fh.write(tabulate(read_df, headers='keys', showindex=False, tablefmt='testile'))
                # read_df.to_csv(output_file, index=None,  sep='\t', mode='a')
                # print read_df.to_html()
                # display(read_df)

            fh.write('\n\n\n\n\nCreated by the Python package "bbcu.reportIlluminaInterop", based on the Python package "interop".\n\n')
