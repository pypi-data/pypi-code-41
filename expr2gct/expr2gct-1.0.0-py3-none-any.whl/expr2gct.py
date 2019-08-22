#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate gct file (version 1.2, for GSEA or ssGSEA) from gene expression matrix file.
note that the gene expression matrix file should be a tab delimited file.
"""
import os
import sys
import argparse
from codecs import open


def check_file_or_directory(file_or_directory):
    """check if the file or directory existed"""
    if os.path.exists(file_or_directory):
        return os.path.abspath(file_or_directory)
    raise argparse.ArgumentTypeError('invalid file or directory: %s' % file_or_directory)


def check_new_file(file_):
    """check if the directory of file existed"""
    directory = os.path.dirname(file_)
    if os.path.exists(directory):
        return os.path.abspath(file_)
    raise argparse.ArgumentTypeError('invalid directory: %s' % directory)


class Expr(object):
    """gene expression"""
    def __init__(self, samples, genes, matrix, desc=None):
        self.samples = samples  # first row
        self.genes = genes  # first column
        self.matrix = matrix
        self.desc = desc

    def set_desc(self, desc):
        self.desc = desc
        return self

    @staticmethod
    def parse_string(string):
        """
        parse gene symbol and expression of this gene from string.
        """
        row = string.rstrip().split('\t')
        return row[0], row[1:]

    @classmethod
    def parse_file(cls, fp):
        """parse Expr instance"""
        # first element is not sample
        samples = fp.readline().rstrip().split('\t')[1:]
        genes = []
        matrix = []
        for line in fp:
            gene, values = cls.parse_string(line)
            genes.append(gene)
            matrix.append(values)
        return cls(samples, genes, matrix)

    @property
    def num_samples(self):
        return len(self.samples)

    @property
    def num_genes(self):
        return len(self.genes)

    @property
    def sample_string(self):
        return '\t'.join(self.samples)

    def get_gene_strings(self):
        return [
            '%s\t%s\t%s' % (
                self.genes[i],
                self.desc[i],
                '\t'.join(row)
            ) for i, row in enumerate(self.matrix)
        ]


def get_args():
    parser = argparse.ArgumentParser('expr2gct')
    parser.add_argument(
        '-e', '--expr', type=check_file_or_directory, required=True,
        help=('Gene expression matrix file(tab delimited only), '
              'first row is sample names, first column is gene symbols')
    )
    parser.add_argument(
        '-d', '--desc', type=check_file_or_directory,
        help=('gct file need DESCRIPTION for column 2 for every gene, '
              'If not provided, default use gene symbol(column 1) instead. '
              'Note that if you provide a DESCRIPTION file, every row reprents a gene. '
              'eg, the first row in DESCRIPTION file represents the first gene in expression file.')
    )
    parser.add_argument('-g', '--gct', required=True, type=check_new_file,
                        help='Where to save gct file')
    return parser.parse_args()


def main():
    args = get_args()
    try:
        with open(args.expr, encoding='utf-8') as fp:
            expr = Expr.parse_file(fp)
            print('Find %d samples, %d genes' % (expr.num_samples, expr.num_genes))
        if args.desc:
            with open(args.desc, encoding='utf-8') as fp:
                desc = [line.rstrip() for line in fp]
        else:
            desc = expr.genes
        assert len(desc) == expr.num_genes
        expr.set_desc(desc)
        with open(args.gct, 'w', encoding='utf-8') as fp:
            fp.write('#1.2\n')
            fp.write('%d\t%d\n' % (expr.num_genes, expr.num_samples))
            fp.write('NAME\tDESCRIPTION\t%s\n' % expr.sample_string)
            for gene_string in expr.get_gene_strings():
                fp.write('%s\n' % gene_string)
    except AssertionError:
        print('Invalid DESCRIPTION file')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
