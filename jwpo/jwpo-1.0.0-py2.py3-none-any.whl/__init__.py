"""Jared Warner's Personalized Opportunitites

Written by Grant Jenks
Copyright 2019

"""

import argparse
import collections
import difflib
import itertools
import logging
import pathlib
import os
import re
import string
import subprocess
import sys
import textwrap

import openpyxl

OUTCOMES_MAP = {
    1: 'ABCD',
    2: 'EUGH',
    3: 'IKLM',
    4: 'OPQR',
}

log = logging.getLogger('jwpo')  # pylint: disable=invalid-name

Label = collections.namedtuple('Label', ['outcome', 'type', 'variant'])
Opportunities = collections.namedtuple(
    'Opportunities',
    ['prolog', 'outcomes', 'problems', 'epilog'],
)


def main(argv=None):
    "Main entry-point for Jared Warner's Personalized Opportunities."
    description = __doc__.splitlines()[0]
    parser = argparse.ArgumentParser('jwpo', description=description)
    parser.add_argument('opportunities_file', type=argparse.FileType('r'))
    parser.add_argument('gradebook_file', type=argparse.FileType('rb'))
    parser.add_argument('opportunity_number', type=int)
    parser.add_argument('opportunity_name')
    parser.add_argument('output_directory')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--verbose', action='store_true')
    group.add_argument('--quiet', action='store_true')

    args = parser.parse_args(argv)
    setup_logging(args)

    log.info("Starting Jared Warner's Personalized Opportunities")
    create_output_dir(args.output_directory)
    opportunities = parse_opportunities_file(args.opportunities_file)
    gradebook = parse_gradebook_file(args.gradebook_file)
    generate_opportunities(args, opportunities, gradebook)
    log.info("Finishing Jared Warner's Personalized Opportunities")


def setup_logging(args):
    "Setup logging."
    if args.verbose:
        level = logging.DEBUG
    elif args.quiet:
        level = logging.WARNING
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(levelname)s:%(message)s',
    )


def create_output_dir(output_directory):
    "Create output directory."
    log.info('Creating output directory: %s', output_directory)
    os.makedirs(output_directory, exist_ok=True)


def parse_opportunities_file(opportunities_file):
    "Parse opportunities file."
    # pylint: disable=too-many-locals,too-many-statements
    log.info('Parsing opportunities file: %s', opportunities_file.name)
    text = opportunities_file.read()
    opportunities_file.close()

    prolog_pattern = re.escape(textwrap.dedent(r'''
        \hrulefill

        %Start questions
    '''))
    prolog_match = re.search(prolog_pattern, text)

    if prolog_match is None:
        log.error('Prolog end not found! Pattern:\n%s', prolog_pattern)
        sys.exit(1)

    prolog = text[:prolog_match.end()]

    outcome_pattern = textwrap.dedent(r'''
        {\\bf (?P<outcome>[A-Z]): (?P<description>.*?)}

        \\begin{itemize}
        (?P<lines>.+?)\\end{itemize}
    ''')
    outcome_matches = list(re.finditer(outcome_pattern, text, re.DOTALL))

    if len(outcome_matches) != 16:
        log.error(
            '%s outcomes found but 16 expected! Pattern:\n%s',
            len(outcome_matches),
            outcome_pattern,
        )
        sys.exit(1)

    outcomes = {
        match.group('outcome'): match.group('description')
        for match in outcome_matches
    }

    problem_pattern = (
        r' *\\item\[(?P<outcome>[A-Z])(?P<type>[0-9])\.(?P<variant>[0-9]):\]\n'
    )
    problems = {}

    for outcome_match in outcome_matches:
        outcome_end = outcome_match.end()
        outcome_outcome = outcome_match.group('outcome')
        outcome_lines = outcome_match.group('lines')
        problem_matches = list(re.finditer(problem_pattern, outcome_lines))
        problem_starts = [match.end() for match in problem_matches]
        problem_ends = [match.start() for match in problem_matches[1:]]
        problem_ends.append(len(outcome_lines))

        for index, problem_match in enumerate(problem_matches):
            problem_outcome = problem_match.group('outcome')

            if outcome_outcome != problem_outcome:
                log.error(
                    'outcome mismatch, %s does not match problem outcome, %s',
                    outcome_outcome,
                    problem_outcome,
                )
                sys.exit(1)

            problem_type = int(problem_match.group('type'))
            problem_variant = int(problem_match.group('variant'))
            label = Label(problem_outcome, problem_type, problem_variant)
            log.debug('Parsed problem: %s, %s, %s', *label)
            text_start = problem_starts[index]
            text_end = problem_ends[index]
            problem_text = outcome_lines[text_start:text_end]
            problems[label] = problem_text.rstrip('\n')

    epilog = text[outcome_end:]

    if not epilog:
        log.error('empty epilog')
        sys.exit(1)

    # Validate that (prolog + outcomes + problems + epilog) == text

    chunks = []

    for outcome, description in outcomes.items():
        chunk = []
        chunk.append(rf'{{\bf {outcome}: {description}}}')
        chunk.append('')
        chunk.append(r'\begin{itemize}')

        for type_, variant in itertools.product(range(1, 4), range(1, 7)):
            label = Label(outcome, type_, variant)

            if label not in problems:
                continue

            chunk.append(rf'    \item[{outcome}{type_}.{variant}:]')
            chunk.append(problems[label])

        chunk.append(r'\end{itemize}')
        chunks.append('\n'.join(chunk))

    parts = [prolog, '\n\n\\hrulefill\n\n'.join(chunks), epilog]
    output = '\n'.join(parts)

    if text != output:
        log.error('Parsing failed, differences below:')
        sys.stdout.writelines(difflib.context_diff(
            text.splitlines(True),
            output.splitlines(True),
        ))
        sys.exit(1)

    opportunities = Opportunities(prolog, outcomes, problems, epilog)
    return opportunities


def parse_gradebook_file(gradebook_file):
    "Parse gradebook file."
    log.info('Parsing gradebook file: %s', gradebook_file.name)
    gradebook_file.close()
    workbook = openpyxl.load_workbook(gradebook_file.name)
    worksheet = workbook['MergeData']
    columns = [
        'Last Name', 'First Name', 'Nickname', 'Email',
        'AW', 'A1', 'A2', 'A3', 'AL', 'BW', 'B1', 'B2', 'B3', 'BL',
        'CW', 'C1', 'C2', 'C3', 'CL', 'DW', 'D1', 'D2', 'D3', 'DL',
        'EW', 'E1', 'E2', 'E3', 'EL', 'UW', 'U1', 'U2', 'U3', 'UL',
        'GW', 'G1', 'G2', 'G3', 'GL', 'HW', 'H1', 'H2', 'H3', 'HL',
        'IW', 'I1', 'I2', 'I3', 'IL', 'JW', 'J1', 'J2', 'J3', 'JL',
        'KW', 'K1', 'K2', 'K3', 'KL', 'LW', 'L1', 'L2', 'L3', 'LL',
        'MW', 'M1', 'M2', 'M3', 'ML', 'NW', 'N1', 'N2', 'N3', 'NL',
        'OW', 'O1', 'O2', 'O3', 'OL', 'PW', 'P1', 'P2', 'P3', 'PL',
        'QW', 'Q1', 'Q2', 'Q3', 'QL', 'RW', 'R1', 'R2', 'R3', 'RL',
        'SW', 'S1', 'S2', 'S3', 'SL', 'TW', 'T1', 'T2', 'T3', 'TL',
        'Unit1', 'Unit2', 'Unit3', 'Unit4', 'Projects', 'TotScore',
    ]
    top_row = [cell.value for cell in worksheet[1]]

    if top_row != columns:
        log.error(
            'unexpected columns!\nexpected: %s\nobserved: %s',
            columns,
            top_row,
        )
        sys.exit(1)

    gradebook = {}

    for index in itertools.count(start=2):
        row = [cell.value for cell in worksheet[index]]

        if all(value is None for value in row):
            break

        key = f'{index:03d}'
        row[4:] = map(int, row[4:])
        data = dict(zip(columns, row))
        last_name = data['Last Name']
        first_name = data['First Name']
        log.debug('Parsed student: %s %s, %s', key, last_name, first_name)
        gradebook[key] = dict(zip(columns, row))

    return gradebook


def generate_opportunities(args, opportunities, gradebook):
    "Generate opportunities."
    # pylint: disable=too-many-locals
    output_directory = args.output_directory
    opportunity_number = args.opportunity_number
    opportunity_name = args.opportunity_name
    log.info('Generating opportunities in %s', output_directory)
    log.info('Using opportunity number: %d', opportunity_number)
    log.info('Using opportunity name: %s', opportunity_name)
    output_dir = pathlib.Path(output_directory)

    for key, data in gradebook.items():
        log.debug('Generating opportunity: %s', key)
        nick = data['Nickname']
        last = data['Last Name']
        student_name = f'{nick} {last}'
        filename = f'{key}-{nick}-{last}'.lower()
        filename = ''.join(char if char.isalnum() else '-' for char in filename)

        # Identify valid problems.

        labels = set()

        # Add labels for given opportunity number.

        for outcome in OUTCOMES_MAP.get(opportunity_number, []):
            for type_ in range(1, 4):
                label = Label(outcome, type_, opportunity_number)
                labels.add(label)

        # Add labels when homework is completed and max points not achieved.

        for number in range(1, opportunity_number + 1):
            for outcome in OUTCOMES_MAP.get(number, []):
                tex_outcome = 'F' if outcome == 'U' else outcome

                if data[f'{outcome}W'] == 0:
                    continue

                type_points = [2, 1, 1]

                for type_, max_points in enumerate(type_points, start=1):
                    if data[f'{outcome}{type_}'] < max_points:
                        label = Label(tex_outcome, type_, opportunity_number)
                        labels.add(label)

        # Generate opportunity TeX file.

        output = generate_opportunity(
            student_name,
            opportunity_name,
            opportunities,
            labels,
        )
        tex_path = output_dir / f'{filename}.tex'

        with open(tex_path, 'w') as writer:
            writer.write(output)

        # Convert to PDF and save to output directory.

        command = [
            'pdflatex',
            '--output-directory',
            output_dir,
            tex_path,
        ]
        log.debug('Running: $ %s', ' '.join(map(str, command)))
        subprocess.run(
            command,
            check=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        )


def generate_opportunity(student_name, opportunity_name, opportunities, labels):
    "Generate opportunity output."
    # pylint: disable=too-many-locals
    prolog, outcomes, problems, epilog = opportunities
    prolog = prolog.replace('student-Name', student_name)
    prolog = prolog.replace('opportunityName', opportunity_name)
    chunks = []

    for outcome, description in outcomes.items():
        items = []

        for type_, variant in itertools.product(range(1, 4), range(1, 7)):
            label = Label(outcome, type_, variant)

            if label not in labels:
                continue

            items.append(label)

        if not items:
            continue

        chunk = []
        chunk.append(rf'{{\bf {outcome}: {description}}}')
        chunk.append('')
        chunk.append(r'\begin{itemize}')

        for item_outcome, type_, _ in items:
            chunk.append(rf'    \item[{item_outcome}{type_}:]')
            chunk.append(problems[label])

        chunk.append(r'\end{itemize}')
        chunks.append('\n'.join(chunk))

    parts = [prolog, '\n\n\\hrulefill\n\n'.join(chunks), epilog]
    output = '\n'.join(parts)
    return output


__title__ = "Jared Warner's Personalized Opportunities"
__version__ = '1.0.0'
__build__ = 0x010000
__author__ = 'Grant Jenks'
__license__ = 'Apache 2.0'
__copyright__ = '2019, Grant Jenks'
