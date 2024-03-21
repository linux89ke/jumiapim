import streamlit as st
import pandas as pd

# Function to concatenate uploaded CSV files
def concatenate_csv_files(files):
    df_list = []
    for file in files:
        try:
            df = pd.read_csv(file)
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
            csv_data = combined_df.to_csv(index=False)
            st.download_button(label="Download Combined CSV", data=csv_data, file_name="combined_file.csv", mime="text/csv")
        else:
            st.error("No valid CSV files uploaded.")

if __name__ == "__main__":
    main()
