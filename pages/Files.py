import streamlit as st
import pandas as pd

def merge_csv_files(output_file, uploaded_files):
    merged_df = pd.concat([pd.read_csv(file)[["SellerName", "Name", "Brand", "PrimaryCategory"]] for file in uploaded_files], ignore_index=True)
    return merged_df

def add_seller_id(merged_df):
    sellers_df = pd.read_excel("sellers.xlsx")
    merged_df = merged_df.merge(sellers_df[['SellerName', 'Seller_ID']], on='SellerName', how='left')
    return merged_df

def main():
    st.title("CSV Files Merger")
    
    uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type='csv')
    if uploaded_files:
        st.write("CSV files uploaded successfully!")
        
        output_file = st.text_input("Enter the name of the output file:", "merged_output.csv")
        
        if st.button("Merge CSV files"):
            merged_df = merge_csv_files(output_file, uploaded_files)
            merged_df_with_seller_id = add_seller_id(merged_df)
            st.dataframe(merged_df_with_seller_id)
            
            # Download button for the merged DataFrame
            csv = merged_df_with_seller_id.to_csv(index=False)
            st.download_button(label="Download CSV", data=csv, file_name=output_file, mime='text/csv')

if __name__ == "__main__":
    main()
