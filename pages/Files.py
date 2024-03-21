import streamlit as st
import pandas as pd
from datetime import datetime

def merge_csv_files(output_file, uploaded_files):
    # Merge the uploaded CSV files
    merged_df = pd.concat([pd.read_csv(file) for file in uploaded_files], ignore_index=True)
    
    # Write the merged DataFrame to a CSV file
    merged_df.to_csv(output_file, index=False)

    return output_file

def main():
    st.title("Merge CSV Files")

    # Upload multiple CSV files
    uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type="csv")

    if uploaded_files:
        # Merge the uploaded files when the user clicks the button
        if st.button("Merge CSV Files"):
            output_file = f"Merged_files_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
            merged_file_path = merge_csv_files(output_file, uploaded_files)
            st.success(f"CSV files merged successfully! Download the merged file below.")
            st.download_button(label="Download Merged File", data=open(merged_file_path, "rb").read(), file_name=output_file)
        
if __name__ == "__main__":
    main()
