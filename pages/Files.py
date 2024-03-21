import streamlit as st
import pandas as pd
import base64

def merge_csv_files(output_file, sellers_df, category_tree_df, uploaded_files):
    # Concatenate uploaded CSV files
    all_data = pd.concat([pd.read_csv(file, delimiter=';', dtype=str) for file in uploaded_files])
    
    # Merge with sellers_df and category_tree_df
    merged_df = pd.merge(all_data, sellers_df, on='SellerName', how='left')
    merged_df = pd.merge(merged_df, category_tree_df, on='PrimaryCategory', how='left')
    
    # Write merged data to a new CSV file
    merged_df.to_csv(output_file, index=False)

def main():
    st.title("CSV File Merger")
    
    # File upload section
    st.subheader("Upload Files to Merge")
    uploaded_files = st.file_uploader("Choose CSV files to merge", accept_multiple_files=True)
    
    if uploaded_files:
        output_file = "Merged_skus_date.csv"
        
        # Display uploaded files
        st.subheader("Uploaded Files:")
        for file in uploaded_files:
            st.write(file.name)
        
        # Merge files when the user clicks the button
        if st.button("Merge Files"):
            sellers_df = pd.read_csv("Sellers.csv", delimiter=';', dtype=str)
            category_tree_df = pd.read_csv("Category_Tree.csv", delimiter=';', dtype=str)
            
            merge_csv_files(output_file, sellers_df, category_tree_df, uploaded_files)
            st.success(f"Files merged successfully! Result saved as {output_file}")
            
            # Download link for the merged file
            st.subheader("Download Merged File:")
            st.markdown(get_binary_file_downloader_html(output_file), unsafe_allow_html=True)

def get_binary_file_downloader_html(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{file_path}">Click here to download {file_path}</a>'
    return href

if __name__ == "__main__":
    main()
