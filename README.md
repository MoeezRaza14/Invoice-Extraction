# CSV Data Extractor

This project is a Streamlit-based application that processes CSV files to extract structured table data and non-table data. The extracted data is displayed within the app and also formatted into a JSON structure for further use.

## Features

- **Extract Table Data**: Automatically identifies and extracts tabular data from CSV files, even with multi-level headers.
- **Identify Headers**: Detects headers by searching for common patterns (e.g., 'Description', 'Qty', 'Quantity', etc.).
- **Add Columns**: Adds two additional columns to the extracted table: 'Package Type' and 'Reference Number', based on detected keywords.
- **Handle Non-Table Data**: Separates non-tabular data and displays it in a structured format.
- **JSON Formatting**: The extracted data (both table and non-table) is converted into a JSON format and displayed within the application.
- **Streamlit App**: The application allows users to upload multiple CSV files for processing.

## Requirements

- Python 3.x
- Required Python libraries:
  - pandas
  - re (regular expressions)
  - os
  - streamlit
  - json

You can install the dependencies using the following command:

```bash
pip install pandas streamlit
```

# **How to Use**
Run the Application: Use the following command to run the Streamlit app locally:

```bash
streamlit run app.py
```
**Upload Files**: Once the app is running, use the interface to upload CSV files for processing.

**View Output**: The app will display both the extracted table data and non-table data. The data will also be shown in JSON format for easy integration with other systems.

# **Code Overview**
**Functions:**
```bash
is_numeric(val): #Checks if a value is numeric.
```
```bash
is_table_row(row_data): #Determines if a row looks like part of a table.
```
```bash
is_header_row(row_data): #Identifies a potential header row using specific keywords.
```
```bash
extract_table_data(df): #Extracts table data and merges multi-level headers.
```
```bash
extract_non_table_data(df): #Extracts rows that do not belong to the table.
```
```bash
add_package_type_and_reference(table_df): #Adds 'Package Type' and 'Reference Number' columns based on keywords.
```
```bash
process_table(df): #Processes the table data and adjusts headers.
```
```bash
process_file(file_path): #Processes a CSV file and returns extracted table and non-table data.
```
```bash
format_json_output(table_df): #Formats the extracted table into JSON.
```

# **Streamlit App:**

Allows users to upload CSV files for processing.
Displays both table and non-table data in a user-friendly manner.
Outputs the data in JSON format.

# **Example**
Once a CSV file is uploaded, the app will extract any table data, add necessary columns, and display it as follows:

```json
{
  "Headers": [
    {"Row": 0, "Column": 0, "Header Name": "Description"},
    {"Row": 0, "Column": 1, "Header Name": "Qty"},
    {"Row": 0, "Column": 2, "Header Name": "Price"}
  ],
  "Rows": [
    {"Row": 1, "Column": 0, "Data": "Item A"},
    {"Row": 1, "Column": 1, "Data": "10"},
    {"Row": 1, "Column": 2, "Data": "100.00"}
  ]
}
```
# **File Structure**

```lua
|-- app.py
|-- README.md
```
**app.py:** The main file containing all the code to run the Streamlit app.
**README.md:** Documentation for the project.

# **Notes**
The app assumes that the CSV files have a general tabular structure. It may not work correctly with files that deviate too much from this format.
If a file contains multiple table-like structures, only the first detected table will be extracted.
