import csv
import glob
import os
import pandas as pd
import xlrd
import re

BGN_TO_EUR = 1.95583
amount = 'amount_eur'
currency = 'cents_in_origin_currency'


def get_account_currency(xls_file):
    workbook = xlrd.open_workbook(xls_file)
    sheet = workbook.sheet_by_index(0)
    return sheet.cell(2, 3).value  # row 2, col 3 is the account currency (e.g. 'BGN' or 'EUR')


def convert_xls_to_csv(xls_file, csv_file):
    workbook = xlrd.open_workbook(xls_file)
    sheet = workbook.sheet_by_index(0)
    print("initial sheet has " + str(sheet.nrows) + " rows")

    with open(csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for row in sheet.get_rows():
            clean_row = [cell.value for cell in row]
            writer.writerow(clean_row)


def clean_top_and_rename_columns(input_file, output_file):
    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        # Skip the first 9 lines.
        for _ in range(9):
            next(reader)

        headers = next(reader)
        # Rename the headers.
        new_header_names = {
            'Вальор:': 'date',
            'Дебит:': amount,
            'Документ:': 'document',
            'Получател/Наредител:': currency,
            'Основание за плащане:': 'description',
        }

        transformed_headers = [new_header_names.get(header) if new_header_names.get(header) else header for header in
                               headers]

        with open(output_file, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(transformed_headers)
            for row in reader:
                writer.writerow(row)

def convert_bgn_to_eur(input_file, output_file):
    data = pd.read_csv(input_file)
    data[amount] = (data[amount] / BGN_TO_EUR).round(2)
    data.to_csv(output_file, index=False)


def consolidate_useful_columns(input_file, output_file):
    """
    When the `currency` column does not contain the currency in the regex format `[A-Z]{3}\s\d+`, this function will
    add the `currency` text to the `description` column.
    """
    data = pd.read_csv(input_file)

    # Define the regex pattern
    pattern = re.compile(r'[A-Z]{3}\s\d+')

    # Apply the function to each row
    for index, row in data.iterrows():
        if not pattern.match(str(row[currency])):
            data.loc[index, 'description'] = str(data.loc[index, 'description']) + ' ' + str(row[currency]) + ' ' + str(row['document'])
            data.loc[index, currency] = data.loc[index, amount]

    # Write the DataFrame to the output CSV file
    data.to_csv(output_file, index=False)


def drop_columns(input_file, output_file):
    """
  Drops the specified columns from a CSV file.

  Args:
    input_file: The input CSV file.
    output_file: The output CSV file.
  """

    data = pd.read_csv(input_file)
    # drop lines with no amount or currency
    data = data[pd.notnull(data[amount])]
    data = data[pd.notnull(data[currency])]
    # drop lines with 'description' that contains 'зареждане' or 'захранване'
    data = data[~data['description'].str.contains('зареждане')]

    column_names = list(data.columns.values)
    columns_to_keep = ['date', amount, currency, 'description']
    columns_to_drop = [col for col in column_names if col not in columns_to_keep]
    for col_to_drop in columns_to_drop:
        data.drop(col_to_drop, inplace=True, axis=1)

    data.to_csv(output_file, index=False)


def prepare_date_format_for_pandas(input_file, output_file):
    data = pd.read_csv(input_file)
    data['date'] = pd.to_datetime(data['date'].astype(str), format='%d/%m/%Y')
    data.to_csv(output_file, index=False)


def _process_single_xls(xls_file, prefix):
    """Run one XLS file through the pipeline up to (and including) drop_columns.
    Returns the path to the resulting CSV."""
    csv_file = f'{prefix}-1-initial.csv'
    convert_xls_to_csv(xls_file, csv_file)

    account_currency = get_account_currency(xls_file)
    print(f"  Account currency: {account_currency}")

    cleaned = f'{prefix}-2-cleaned.csv'
    clean_top_and_rename_columns(csv_file, cleaned)

    if account_currency == 'BGN':
        print("  Converting BGN → EUR...")
        converted = f'{prefix}-2b-converted_to_eur.csv'
        convert_bgn_to_eur(cleaned, converted)
        cleaned = converted

    consolidated = f'{prefix}-3-consolidated.csv'
    consolidate_useful_columns(cleaned, consolidated)

    dropped = f'{prefix}-4-dropped.csv'
    drop_columns(consolidated, dropped)

    n = len(pd.read_csv(dropped))
    print(f"  {n} transactions after filtering")
    return dropped


def transform_folder(input_folder):
    xls_files = sorted(glob.glob(os.path.join(input_folder, '*.xls')))
    if not xls_files:
        raise ValueError(f"No .xls files found in {input_folder}")

    print(f"Found {len(xls_files)} file(s): {[os.path.basename(f) for f in xls_files]}")

    per_file_csvs = []
    for xls_file in xls_files:
        stem = os.path.splitext(os.path.basename(xls_file))[0]
        prefix = os.path.join('output', stem)
        print(f"Processing {os.path.basename(xls_file)} ...")
        per_file_csvs.append(_process_single_xls(xls_file, prefix))

    combined_path = 'output/4-combined.csv'
    combined = pd.concat([pd.read_csv(f) for f in per_file_csvs])
    combined.to_csv(combined_path, index=False)
    print(f"Combined total: {len(combined)} transactions across {len(xls_files)} file(s)")

    ready_to_import = 'output/5-ready_to_import.csv'
    prepare_date_format_for_pandas(combined_path, ready_to_import)

    return ready_to_import

