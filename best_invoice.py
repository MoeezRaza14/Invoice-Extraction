# -*- coding: utf-8 -*-
"""Best Invoice.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1c2Hfr9h3IH3UgS3y_TN1ZNNN87NRSAeq
"""

import pandas as pd
import re
import os
from tabulate import tabulate

df = pd.read_csv("your_file.csv", header=None)
df

def is_numeric(val):
    """ Check if a value is numeric (either int or float). """
    try:
        float(val.replace(',', ''))  # Remove commas and attempt to cast to float
        return True
    except ValueError:
        return False

def is_table_row(row_data):
    """Determine if a row looks like part of a table by checking for multiple numeric values."""
    # **Exclude rows containing 'Total' or 'TTL' if they are part of the table.**
    if any(re.search(r'total|ttl', str(item), re.IGNORECASE) for item in row_data if pd.notna(item)):
        return False  # Exclude rows with 'Total' or 'TTL'

    # A row is considered part of a table if it has at least 2 numeric values
    numeric_count = sum(is_numeric(item) for item in row_data if pd.notna(item))
    return numeric_count >= 2

def is_header_row(row_data):
    """Check if a row contains 'Qty', 'Quantity', or 'Quantities' in any case."""
    # **Ensure that 'Total' in header rows does not lead to exclusion.**
    header_pattern = re.compile(r'description|desc.|desc|qty|quantity|quantities', re.IGNORECASE)  # Kept 'total' out
    return any(header_pattern.search(str(item)) for item in row_data if pd.notna(item))

def extract_table_data(df):
    """Extract table data from the dataframe, including rows with multi-level headers."""
    table_data = []
    header_row = None
    header_index = None
    next_row_as_header = False  # Track if next row should be treated as part of the header

    for index, row in df.iterrows():
        row_data = row.tolist()
        row_data = [item if pd.notna(item) else None for item in row_data]
        row_length = len(row_data)

        # Skip rows that don't have at least 2 non-NaN items
        if row_length < 2:
            continue

        # If we detect a header row, mark the next row to be treated as sub-headers
        if header_row is None and is_header_row(row_data):
            header_row = row_data
            header_index = index
            next_row_as_header = True  # Mark next row as a potential sub-header
            continue

        # **Updated logic for multi-level headers**
        # Check if the next row is part of the table or not before concatenating with the header row
        if next_row_as_header:
            next_row_as_header = False  # Reset for subsequent iterations

            # If the next row is not part of the table, concatenate it with the header row
            if not is_table_row(row_data):
                for i in range(len(row_data)):
                    if pd.notna(row_data[i]):  # Only concatenate non-NaN values
                        header_row[i] = f"{header_row[i]} {row_data[i]}" if header_row[i] else row_data[i]
                continue

        # If header is already detected, start adding table rows
        if header_row:
            if is_table_row(row_data):
                table_data.append(row_data)

    # Ensure the header row is handled correctly for missing values or 'None'
    if header_row:
        table_df = pd.DataFrame(table_data, columns=header_row)

        # Handle remaining 'None' or NaN in headers
        for idx, value in enumerate(header_row):
            if value is None:
                next_row_index = header_index + 1
                if next_row_index < len(df):
                    next_row = df.iloc[next_row_index]
                    if not is_table_row(next_row.tolist()):
                        header_row[idx] = next_row[idx] if idx < len(next_row) else None

        # Replace remaining 'None' with 'Unnamed: x'
        unnamed_count = 1
        updated_header_row = []
        for item in header_row:
            if pd.isna(item) or item is None:
                updated_header_row.append(f'Unnamed: {unnamed_count}')
                unnamed_count += 1
            else:
                updated_header_row.append(item)

        table_df = pd.DataFrame(table_data, columns=updated_header_row)
    else:
        table_df = pd.DataFrame()

    return table_df

def extract_non_table_data(df):
    """Extract non-table data from the dataframe, including rows that are not part of the table."""
    non_table_data = []

    for index, row in df.iterrows():
        row_data = row.tolist()
        row_data = [item if pd.notna(item) else None for item in row_data]
        row_length = len(row_data)

        if row_length < 2:
            non_table_data.append(row_data)

    non_table_df = pd.DataFrame(non_table_data) if non_table_data else pd.DataFrame()

    return non_table_df

def add_package_type_and_reference(table_df):
    """Add 'Package Type' and 'Reference Number' columns to the table."""
    table_df['Package Type'] = None
    table_df['Reference Number'] = None

    package_keywords = ['ctn', 'ctns', 'Palette', 'Palettes', 'Box', 'boxes', 'Case', 'cases', 'EuroPalette', 'EuroPalettes']

    for keyword in package_keywords:
        if any(keyword.lower() in str(header).lower() for header in table_df.columns):
            table_df['Package Type'] = keyword.upper()
            break

def process_table(df):
    """Process table data by extracting relevant rows, adjusting headers, and adding additional columns."""
    table_df = extract_table_data(df)
    add_package_type_and_reference(table_df)

    # **New Logic for Removing Empty 'Unnamed' Columns**
    unnamed_columns = [col for col in table_df.columns if str(col).startswith('Unnamed')]

    for col in unnamed_columns:
        if table_df[col].isna().all():  # Check if the entire column is empty (NaN)
            table_df.drop(columns=[col], inplace=True)  # Drop the column if it's empty

    # **New Logic for Handling Duplicate Column Names**
    # Create a dictionary to track the count of each column name
    column_counts = {}
    new_columns = []

    for col in table_df.columns:
        if col in column_counts:
            # Increment count for this column name and rename it
            column_counts[col] += 1
            new_columns.append(f"{col} {column_counts[col]}")
        else:
            # First occurrence of this column name
            column_counts[col] = 1
            new_columns.append(col)

    # Assign the updated column names
    table_df.columns = new_columns

    return table_df

def process_multiple_files(file_paths):
    for file_path in file_paths:
        extension = os.path.splitext(file_path)[1].lower()

        # Only handle CSV files directly
        if extension not in ['.csv']:
            print(f"Skipping file {file_path} as it is not a CSV file.")
            continue

        print(f"\nProcessing file: {file_path}\n")
        try:
            df = pd.read_csv(file_path, header=None, dtype=str)
            table_df = process_table(df)
            non_table_df = extract_non_table_data(df)

            if not table_df.empty:
                print(f"\nExtracted table data from {file_path}:\n")
                print(tabulate(table_df, headers='keys', tablefmt='grid'))
            else:
                print(f"No table data found in the file: {file_path}")

            if not non_table_df.empty:
                print(f"\nNon-table data from {file_path}:\n")
                print(non_table_df)
            else:
                print(f"No non-table data found in the file: {file_path}")

        except ValueError as e:
            print(e)

paths = [
    "file1.csv",
    "file2.csv",
    "file3.csv",
    "file4.csv"
]

process_multiple_files(paths)
