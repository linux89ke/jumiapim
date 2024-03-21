import streamlit as st
import pandas as pd

def merge_csv_files(output_file, uploaded_files):
    merged_df = pd.concat([pd.read_csv(file) for file in uploaded_files], ignore_index=True)
    merged_df.to_csv(output_file, index=False)

def add_seller_id(merged_df, sellers_df):
    merged_df['SellerID'] = merged_df['SellerName'].map(sellers_df.set_index('SellerName')['Seller_ID'])

def filter_columns(merged_df):
    return merged_df[['SellerName', 'Name', 'Brand', 'PrimaryCategory', 'SellerID']]

def main():
    st.title("Merge and Filter CSV Files")

    uploaded_files = st.file_uploader("Upload CSV Files to Merge", accept_multiple_files=True)
    if uploaded_files:
        output_file = "merged_files.csv"
        merge_csv_files(output_file, uploaded_files)
        st.success("CSV files merged successfully!")

        st.subheader("Upload Sellers Excel File")
        sellers_excel_file = st.file_uploader("Upload Sellers Excel File", type=['xlsx'])
        if sellers_excel_file is not None:
            sellers_df = pd.read_excel(sellers_excel_file)
            add_seller_id(merged_df, sellers_df)
            filtered_df = filter_columns(merged_df)
            st.write(filtered_df)

            st.markdown(get_csv_download_link(filtered_df, "Filtered_Result"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
