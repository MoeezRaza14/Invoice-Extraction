import pandas as pd
import re
import os
import json
import streamlit as st
from tabulate import tabulate

def is_numeric(val):
    try:
        float(val.replace(',', ''))
        return True
    except ValueError:
        return False

def is_table_row(row_data):
    numeric_count = sum(is_numeric(item) for item in row_data if pd.notna(item))
    if any(re.search(r'\btotal\b|\btotal\w*|\bttl\b', str(item), re.IGNORECASE) for item in row_data):
        return False
    return numeric_count >= 2

def is_header_row(row_data):
    header_pattern = re.compile(r'description|desc.|desc|qty|quantity|quantities', re.IGNORECASE)
    return any(header_pattern.search(str(item)) for item in row_data if pd.notna(item))

def extract_table_data(df):
    table_data = []
    header_row = None
    header_index = None
    next_row_as_header = False

    for index, row in df.iterrows():
        row_data = row.tolist()
        row_data = [item if pd.notna(item) else None for item in row_data]
        row_length = len(row_data)

        if row_length < 2:
            continue

        if header_row is None and is_header_row(row_data):
            header_row = row_data
            header_index = index
            next_row_as_header = True
            continue

        if next_row_as_header:
            next_row_as_header = False
            if not is_table_row(row_data):
                for i in range(len(row_data)):
                    if pd.notna(row_data[i]):
                        header_row[i] = f"{header_row[i]} {row_data[i]}" if header_row[i] else row_data[i]
                continue

        if header_row:
            if is_table_row(row_data):
                table_data.append(row_data)

    if header_row:
        table_df = pd.DataFrame(table_data, columns=header_row)
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
    table_df['Package Type'] = None
    table_df['Reference Number'] = None
    package_keywords = ['ctn', 'ctns', 'Palette', 'Palettes', 'Box', 'boxes', 'Case', 'cases', 'EuroPalette', 'EuroPalettes']
    for keyword in package_keywords:
        if any(keyword.lower() in str(header).lower() for header in table_df.columns):
            table_df['Package Type'] = keyword.upper()
            break

def process_table(df):
    table_df = extract_table_data(df)
    add_package_type_and_reference(table_df)
    unnamed_columns = [col for col in table_df.columns if str(col).startswith('Unnamed')]
    for col in unnamed_columns:
        if table_df[col].isna().all():
            table_df.drop(columns=[col], inplace=True)
    column_counts = {}
    new_columns = []
    for col in table_df.columns:
        if col in column_counts:
            column_counts[col] += 1
            new_columns.append(f"{col} {column_counts[col]}")
        else:
            column_counts[col] = 1
            new_columns.append(col)
    table_df.columns = new_columns
    return table_df

def create_json_output(table_df):
    output = {
        "Headers": [],
        "Rows": []
    }
    for col_idx, header_name in enumerate(table_df.columns):
        output["Headers"].append({
            "Row": 0,
            "Column": col_idx,
            "Header Name": str(header_name)
        })
    for row_idx, row in table_df.iterrows():
        for col_idx, cell in enumerate(row):
            output["Rows"].append({
                "Row": row_idx,
                "Column": col_idx,
                "Text": str(cell)
            })
    return json.dumps(output, indent=4)

def process_file(uploaded_file):
    df = pd.read_csv(uploaded_file, header=None, dtype=str)
    table_df = process_table(df)
    non_table_df = extract_non_table_data(df)
    return table_df, non_table_df

def format_json_output(table_df):
    return create_json_output(table_df)