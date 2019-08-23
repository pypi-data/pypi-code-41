class QualityMetricHelper:
    def make_idr_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'IDRQualityMetric'):
            return
        qc = self.backend.read_json(self.analysis.get_files('qc_json')[0])
        idr_qc = qc['idr_frip_qc']
        replicate = self.get_bio_replicate(encode_file)
        rep_pr = idr_qc['rep' + replicate + '-pr']
        frip_score = rep_pr['FRiP']
        idr_peaks = qc['ataqc']['rep' + replicate]['IDR peaks'][0]
        qc_object = {}
        qc_object['F1'] = frip_score
        qc_object['N1'] = idr_peaks
        idr_cutoff = self.analysis.metadata['inputs']['atac.idr_thresh']
        # Strongly expects that plot exists
        plot_png = self.analysis.search_up(gs_file.task,
                                           'idr_pr',
                                           'idr_plot')[0]
        qc_object.update({
            'IDR_cutoff':                           idr_cutoff,
            'IDR_plot_rep{}_pr'.format(replicate):  self.get_attachment(plot_png, 'image/png')})
        return self.queue_qc(qc_object,
                             encode_file,
                             'idr-quality-metrics')

    def make_flagstat_qc(self, encode_bam_file, gs_file):
        # Return early if qc metric exists
        if self.file_has_qc(encode_bam_file, 'SamtoolsFlagstatsQualityMetric'):
            return
        qc = self.backend.read_json(self.analysis.get_files('qc_json')[0])
        replicate = self.get_bio_replicate(encode_bam_file)
        flagstat_qc = qc['nodup_flagstat_qc']['rep' + replicate]
        for key, value in flagstat_qc.items():
            if '_pct' in key:
                flagstat_qc[key] = '{}%'.format(value)
        return self.queue_qc(flagstat_qc,
                             encode_bam_file,
                             'samtools-flagstats-quality-metric')

    def make_cross_correlation_qc(self, encode_bam_file, gs_file):
        # Return early if qc metric exists
        if self.file_has_qc(encode_bam_file, 'ComplexityXcorrQualityMetric'):
            return
        qc = self.backend.read_json(self.analysis.get_files('qc_json')[0])
        plot_pdf = self.analysis.search_down(gs_file.task,
                                             'xcor',
                                             'plot_pdf')[0]
        read_length_file = self.analysis.search_up(gs_file.task,
                                                   'bowtie2',
                                                   'read_len_log')[0]
        read_length = int(self.backend.read_file(read_length_file.filename).decode())
        replicate = self.get_bio_replicate(encode_bam_file)
        xcor_qc = qc['xcor_score']['rep' + replicate]
        pbc_qc = qc['pbc_qc']['rep' + replicate]
        xcor_object = {
            'NRF':                  pbc_qc['NRF'],
            'PBC1':                 pbc_qc['PBC1'],
            'PBC2':                 pbc_qc['PBC2'],
            'NSC':                  xcor_qc['NSC'],
            'RSC':                  xcor_qc['RSC'],
            'sample size':          xcor_qc['num_reads'],
            "fragment length":      xcor_qc['est_frag_len'],
            "paired-end":           self.analysis.metadata['inputs']['atac.paired_end'],
            "read length":          read_length,
            "cross_correlation_plot": self.get_attachment(plot_pdf, 'application/pdf')
        }
        return self.queue_qc(xcor_object,
                             encode_bam_file,
                             'complexity-xcorr-quality-metrics')

    def make_star_qc_metric(self, encode_bam_file, gs_file):
        if self.file_has_qc(encode_bam_file, 'StarQualityMetric'):
            return
        qc_file = self.analysis.get_files(filename=gs_file.task.outputs['star_qc_json'])[0]
        qc = self.backend.read_json(qc_file)
        star_qc_metric = qc.get('star_qc_metric')
        del star_qc_metric['Started job on']
        del star_qc_metric['Started mapping on']
        del star_qc_metric['Finished on']
        for key, value in star_qc_metric.items():
            star_qc_metric[key] = string_to_number(value)
        return self.queue_qc(star_qc_metric,
                             encode_bam_file,
                             'star-quality-metric')

    def make_microrna_quantification_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'MicroRnaQuantificationQualityMetric'):
            return
        qc_file = self.analysis.get_files(filename=gs_file.task.outputs['star_qc_json'])[0]
        qc = self.backend.read_json(qc_file)
        expressed_mirnas_qc = qc['expressed_mirnas']
        return self.queue_qc(expressed_mirnas_qc,
                             encode_file,
                             'micro-rna-quantification-quality-metric')

    def make_microrna_mapping_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'MicroRnaMappingQualityMetric'):
            return
        qc_file = self.analysis.get_files(filename=gs_file.task.outputs['star_qc_json'])[0]
        qc = self.backend.read_json(qc_file)
        aligned_reads_qc = qc['aligned_reads']
        return self.queue_qc(aligned_reads_qc,
                             encode_file,
                             'micro-rna-mapping-quality-metric')

    def make_microrna_correlation_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'CorrelationQualityMetric'):
            return
        qc_file = self.analysis.search_down(gs_file.task,
                                            'spearman_correlation',
                                            'spearman_json')[0]
        qc = self.backend.read_json(qc_file)
        spearman_value = qc['spearman_correlation']['spearman_correlation']
        spearman_correlation_qc = {'Spearman correlation': spearman_value}
        return self.queue_qc(spearman_correlation_qc,
                             encode_file,
                             'correlation-quality-metric',
                             shared=True)

    def make_chip_alignment_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'ChipAlignmentQualityMetric'):
            return
        qc = self.backend.read_json(self.analysis.get_files('qc_json')[0])
        replicate = self.get_bio_replicate(encode_file)
        output_qc = qc['align']['samstat'][replicate]
        for k, v in output_qc.items():
            if k.startswith('pct'):
                output_qc[k] = float(v)
            else:
                output_qc[k] = int(v)
        return self.queue_qc(
            output_qc,
            encode_file,
            'chip-alignment-quality-metric',
        )

    def make_chip_align_enrich_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'ChipAlignmentEnrichmentQualityMetric'):
            return

    def make_chip_library_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'ChipLibraryQualityMetric'):
            return

    def make_chip_replication_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'ChipReplicationQualityMetric'):
            return

    def make_chip_peak_enrichment_qc(self, encode_file, gs_file):
        if self.file_has_qc(encode_file, 'ChipPeakEnrichmentQualityMetric'):
            return
