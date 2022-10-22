# coding: utf-8

import sys, os, argparse, csv


class CSVHandler:

    def __init__(self, file=None):
        self.header = []
        self.rows = []
        self.MIN_FILE_SIZE = 10

        if file:
            self.set_csv(file)

    def _fail_gracefully(function):
        def wrapper(self, *args, **kwargs):
            prev_header = self.header.copy()
            prev_rows = self.rows.copy()

            try:
                return function(self, *args, **kwargs)
            except Exception as e:
                print(e)
                self.header = prev_header
                self.rows = prev_rows
        return wrapper

    @_fail_gracefully
    def set_csv(self, file):
        if self._valid_csv(file):
            with open(file, newline='') as csv_file:
                try:
                    reader = csv.reader(csv_file)
                    field_length = len(next(reader))
                    csv_file.seek(0)

                    if self._has_header(csv_file):
                        self.header = [field.strip() for field in next(reader)]

                    for row in reader:
                        if len(row) != field_length:
                            raise Exception('Inconsistent row length: file \'{}\', line {}'.format(file, reader.line_num))

                        self.rows.append([field.strip() for field in row])

                except csv.Error as e:
                    raise Exception('file \'{}\', line {}: {}'.format(file, reader.line_num, e))
        else:
            raise Exception('Invalid file: \'{}\''.format(file))

    def print_csv(self, field=None):
        def print_rows(rows):
            for row in rows:
                print('\t'.join(field for field in row))

        if field and field not in self.header:
            print('\'{}\' field doesn\'t exist'.format(field))
            return

        if self.header:
            print('\t'.join(self.header))
            print()

        if field:
            print_rows(sorted(self.rows, key=lambda row: row[self.header.index(field)]))
        else:
            print_rows(self.rows)

    def count_occurrences(self, value, field):
        if field not in self.header:
            print('\'{}\' field doesn\'t exist'.format(field))
            return

        field_index = self.header.index(field)
        value = value.lower()

        return len([1 for row in self.rows if value in row[field_index].lower()])

    def average(self, field):
        if field not in self.header:
            print('\'{}\' field doesn\'t exist'.format(field))
            return

        field_index = self.header.index(field)
        values = []

        for value in [row[field_index] for row in self.rows]:
            try:
                values.append(float(value))
            except ValueError:
                pass

        return sum(values) / len(values) if len(values) > 0 else None

    def replace(self, old_val, new_val, field):
        if field not in self.header:
            print('\'{}\' field doesn\'t exist.'.format(field))
            return

        field_index = self.header.index(field)

        for row in self.rows:
            row[field_index] = row[field_index].replace(old_val, new_val)

    def to_file(self, out_file):
        if not out_file.endswith('.csv'):
            print('\'{}\' does not end with csv'.format(out_file))
            return

        if not self.rows:
            print('No data to write.')
            return

        with open(out_file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')

            if self.header:
                writer.writerow(self.header)

            for row in self.rows:
                writer.writerow(row)

    def _has_header(self, csv_file):
        pos = csv_file.tell()
        csv_file.seek(0)
        res = csv.Sniffer().has_header(csv_file.read(2048))
        csv_file.seek(pos)
        return res

    def _valid_csv(self, file):
        return file and os.path.isfile(file) and file.endswith('.csv') and os.path.getsize(file) > self.MIN_FILE_SIZE


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('csv_file', help='the csv file to be parsed')
    group.add_argument('-s', '--sort', action='store_true', help='sort output by a given FIELD')
    group.add_argument('-a', '--average', action='store_true', help='output average of row values in given FIELD')
    group.add_argument('-c', '--count', metavar='VALUE', help='output total occurrences of VALUE in given FIELD (case insensitive)')
    group.add_argument('-r', '--replace', nargs=2, metavar=('OLD', 'NEW'), help='replace instances of OLD value to NEW value in given FIELD')
    parser.add_argument('-o', '--output', metavar='FILE', help='output parsed (possibly modified) csv data to FILE')
    parser.add_argument('-f', '--field', help='FIELD to be associated with other options')

    args = parser.parse_args()

    opt = [k for k,v in vars(args).items() if v and k not in ['csv_file', 'field', 'output']]

    if not args.field and opt:
        print('Must include --field with --{} option.'.format(opt[0]))
        sys.exit()
    elif args.field and not opt:
        print('Must associate option with given --field.')
        sys.exit()


    handler = CSVHandler(args.csv_file)

    if args.count:
        print(handler.count_occurrences(args.count, args.field))
    elif args.average:
        print(handler.average(args.field))
    elif args.replace:
        handler.replace(args.replace[0], args.replace[1], args.field)
    else:
        handler.print_csv(args.field)

    if args.output:
        handler.to_file(args.output)
