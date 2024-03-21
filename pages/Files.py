import streamlit as st
import pandas as pd
import base64

def merge_csv_files(files):
    dfs = []
    for file in files:
        try:
            # Try reading with default configuration
            df = pd.read_csv(file)
            dfs.append(df)
        except pd.errors.ParserError:
            try:
                # Try reading with different delimiter
                df = pd.read_csv(file, delimiter=';')
                dfs.append(df)
            except Exception as e:
                st.error(f"Error reading file {file.name}: {e}")
    if dfs:
        merged_df = pd.concat(dfs, axis=1, join='inner')
        return merged_df
    else:
        return None

def main():
    st.title("CSV File Merger")

    st.sidebar.header("Upload CSV Files")
    uploaded_files = st.sidebar.file_uploader("Upload CSV files", accept_multiple_files=True)

    if uploaded_files:
        st.sidebar.write("Files Uploaded:")
        for file in uploaded_files:
            st.sidebar.write(file.name)

        if st.sidebar.button("Merge CSV Files"):
            merged_df = merge_csv_files(uploaded_files)
            if merged_df is not None:
                st.dataframe(merged_df)

                csv = merged_df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode() 
                href = f'<a href="data:file/csv;base64,{b64}" download="merged_file.csv">Download Merged CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.error("No valid files were uploaded or processed.")

if __name__ == "__main__":
    main()
