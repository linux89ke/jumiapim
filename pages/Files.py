import streamlit as st
import pandas as pd

def merge_csv_files(files):
    dfs = []
    for file in files:
        df = pd.read_csv(file)
        dfs.append(df)
    merged_df = pd.concat(dfs, axis=1, join='inner')
    return merged_df

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
            st.dataframe(merged_df)

            csv = merged_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode() 
            href = f'<a href="data:file/csv;base64,{b64}" download="merged_file.csv">Download Merged CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
