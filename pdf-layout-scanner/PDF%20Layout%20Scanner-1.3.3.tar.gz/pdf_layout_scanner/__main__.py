from . import layout_scanner
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='PDF to TEXT converter', prog='python -m pdf_layout_scanner'
    )
    parser.add_argument('input', type=str, help='input PDF file')
    parser.add_argument('output', type=str, help='output file destination')

    args = parser.parse_args()

    result = layout_scanner.get_pages(args.input)
    with open(args.output, 'w') as f:
        f.write(''.join(result))
