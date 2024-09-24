import streamlit as st
from Processing import process_file, format_json_output  # Import the necessary functions

st.title("CSV Data Extractor")

uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.write(f"Processing file: {uploaded_file.name}")
        try:
            table_df, non_table_df = process_file(uploaded_file)

            # Display extracted table data
            if not table_df.empty:
                st.subheader("Extracted Table Data")
                st.dataframe(table_df)

                # Format JSON output
                json_output = format_json_output(table_df)

                # Convert and display the formatted JSON
                st.subheader("Formatted JSON Output")
                st.json(json_output)  # Display formatted JSON output

            else:
                st.warning(f"No table data found in the file: {uploaded_file.name}")

            # Display non-table data
            if not non_table_df.empty:
                st.subheader("Non-Table Data")
                st.dataframe(non_table_df)

                # Convert non_table_df to JSON and display
                non_table_json = non_table_df.to_json(orient='records')
                st.subheader("Non-Table Data as JSON")
                st.json(non_table_json)  # JSON output of the non-table data

            else:
                st.warning(f"No non-table data found in the file: {uploaded_file.name}")

        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")