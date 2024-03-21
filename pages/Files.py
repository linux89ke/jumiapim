import streamlit as st
import pandas as pd
import os

def merge_csv_files(output_file, uploaded_files):
    merged_df = pd.concat([pd.read_csv(file, delimiter=';') for file in uploaded_files], ignore_index=True)
    merged_df.to_csv(output_file, index=False)  # Save the merged DataFrame to a CSV file
    return merged_df

def main():
    st.title("CSV File Merger")

    # Allow user to upload CSV files
    uploaded_files = st.file_uploader("Upload CSV files to merge", accept_multiple_files=True)

    if uploaded_files:
        output_file = "merged_file.csv"

        # Merge the uploaded CSV files
        merged_df = merge_csv_files(output_file, uploaded_files)

        # Display merged DataFrame
        st.write("Merged DataFrame:")
        st.write(merged_df)

        # Offer download link for the merged CSV file
        st.markdown(f"### [Download merged CSV file]({output_file})")

        # Download button for the merged CSV file
        st.download_button(label="Download merged CSV file", data=open(output_file, "rb").read(), file_name=os.path.basename(output_file), mime="text/csv")

if __name__ == "__main__":
    main()
