import streamlit as st
import pandas as pd

# Function to concatenate uploaded CSV files
def concatenate_csv_files(files):
    common_columns = None
    df_list = []
    
    # Identify common columns among all files
    for file in files:
        try:
            df = pd.read_csv(file, nrows=1, encoding='utf-8-sig')
            if common_columns is None:
                common_columns = set(df.columns)
            else:
                common_columns = common_columns.intersection(df.columns)
        except Exception as e:
            st.warning(f"Could not read file {file.name} because of error: {e}")

    if common_columns is not None:
        # Read files while specifying only common columns
        for file in files:
            try:
                df = pd.read_csv(file, usecols=common_columns, encoding='utf-8-sig')
                df_list.append(df)
            except Exception as e:
                st.warning(f"Could not read file {file.name} because of error: {e}")
    
    if len(df_list) == 0:
        return None
    else:
        return pd.concat(df_list, ignore_index=True)

# Streamlit app
def main():
    st.title("CSV File Combiner")

    # Upload CSV files
    uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)

    if uploaded_files:
        st.write("Uploaded files:")
        for file in uploaded_files:
            st.write(file.name)

        # Concatenate CSV files
        combined_df = concatenate_csv_files(uploaded_files)

        if combined_df is not None:
            st.success("Files successfully combined!")
            st.write("Combined DataFrame:")
            st.write(combined_df)

            # Download combined DataFrame as CSV
            csv_data = combined_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(label="Download Combined CSV", data=csv_data, file_name="combined_file.csv", mime="text/csv")
        else:
            st.error("No valid CSV files uploaded.")

if __name__ == "__main__":
    main()
