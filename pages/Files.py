import streamlit as st
import pandas as pd
import base64

def merge_csv_files(csv_files):
    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        dfs.append(df)
    merged_df = pd.concat(dfs, ignore_index=True)
    return merged_df

def download_link(df, file_name='merged_data.xlsx'):
    excel_file = df.to_excel(index=False)
    excel_file = df.to_excel(index=False)
    excel_bytes = excel_file.getvalue()
    b64 = base64.b64encode(excel_bytes).decode()
    href = f'<a href="data:file/xlsx;base64,{b64}" download="{file_name}">Download Excel file</a>'
    return href

def main():
    st.title('CSV File Merger')

    # File uploader
    st.write("Upload your CSV files")
    csv_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type='csv')

    if csv_files:
        # Merge CSV files
        merged_df = merge_csv_files(csv_files)

        # Show merged DataFrame
        st.write("Merged DataFrame:")
        st.dataframe(merged_df)

        # Provide option to download the merged DataFrame as Excel
        st.markdown(download_link(merged_df), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
