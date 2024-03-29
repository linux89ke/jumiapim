import pandas as pd
from datetime import datetime
import os
import streamlit as st
import base64

# Define a function to process the input and generate output files
def process_files(input_file):
    # Define the output folder
    output_folder = f'PIM_output_{datetime.now().strftime("%Y-%m-%d_%H-%M")}'
    os.makedirs(output_folder, exist_ok=True)
    
    # Check for existing files and generate unique filenames for Pivot and PIM output
    base_output_file = 'Pivot_Date'
    pivot_output_file = f'{base_output_file}_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.csv'
    counter = 1
    while os.path.exists(os.path.join(output_folder, pivot_output_file)):
        pivot_output_file = f'{base_output_file}_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{counter}.csv'
        counter += 1
    
    # Read the file into a DataFrame (handle both Excel and CSV files)
    if input_file.name.endswith('.xlsx') or input_file.name.endswith('.xls'):
        df = pd.read_excel(input_file, engine='openpyxl')
    elif input_file.name.endswith('.csv'):
        try:
            df = pd.read_csv(input_file, encoding='utf-8')
        except UnicodeDecodeError:
            # If UTF-8 encoding fails, try 'latin-1' encoding
            df = pd.read_csv(input_file, encoding='latin-1')
    else:
        st.error("Unsupported file format. Please upload an Excel (.xls, .xlsx) or CSV file.")
        return False
    
    # Specify the column names
    seller_name_col = 'SELLER_NAME'
    category_col = 'CATEGORY'
    app_col = 'app'
    rej_col = 'rej'
    reason_col = 'reason'
    
    # Replace blank values in the 'reason' column with ''
    df[reason_col] = df[reason_col].fillna('')
    
    # Map values under 'reason' to the desired replacements
    reason_mapping = {
        'col': '1000005 - Kindly confirm the actual product colour',
        'cat': '1000004 - Wrong Category',
        'var': '1000038 - Kindly Ensure ALL Sizes Of This Product Are Created As Variants Under This Product & Not Created As Unique Products',
        'bra': '1000007 - Other Reason',
        
    }
    
    # Create a pivot table without totals
    pivot_table = pd.pivot_table(df,
                                 values=[app_col, rej_col],
                                 index=[seller_name_col, category_col, reason_col],
                                 aggfunc='count',
                                 fill_value=0)
    
    # Reset index to create a DataFrame from the pivot table
    table_df = pivot_table.reset_index()
    
    # Melt the DataFrame to convert it to the desired format
    melted_df = pd.melt(table_df, id_vars=[seller_name_col, category_col, reason_col],
                        var_name='type', value_name='count')
    
    # Filter rows with non-empty 'count' values
    melted_df = melted_df[melted_df['count'] != 0]
    
    # Pivot the melted DataFrame to get separate columns for app and rej counts
    final_df = melted_df.pivot_table(index=['SELLER_NAME', 'CATEGORY', 'reason'],
                                     columns='type', values='count', fill_value='').reset_index()
    
    # Custom sorting function to keep the original case for 'Wrong Variation - means size only'
    def custom_sort(x):
        return ('' if x == '' else x.lower(), x)
    
    # Sort 'reason' column with blanks first and then alphabetically using the custom sorting function
    final_df['reason'] = final_df['reason'].apply(lambda x: '' if x == '' else x)
    final_df.sort_values(by='reason', inplace=True, key=lambda x: x.map(custom_sort) if x.dtype == 'O' else x)
    
    # Apply the updated reason mapping to the 'reason' column
    final_df['reason'] = final_df['reason'].map(reason_mapping)
    
    # Create a new datetime column
    final_df['Date_Column'] = datetime.now().strftime('%Y-%m-%d')
    
    # Add two columns before 'SELLER_NAME' with week number and formatted date
    final_df.insert(0, 'Week_Number', pd.to_datetime(final_df['Date_Column']).dt.isocalendar().week)
    final_df.insert(1, 'Formatted_Date', pd.to_datetime(final_df['Date_Column']).dt.strftime('%m/%d/%Y'))
    
    # Add two columns after 'rej' with 'KE' and 'Charles'
    final_df.insert(final_df.columns.get_loc('rej') + 1, 'new_col_1', 'KE')
    final_df.insert(final_df.columns.get_loc('rej') + 2, 'new_col_2', 'Charles')
    
     # Add a blank column after 'rej'
    final_df.insert(final_df.columns.get_loc('rej') + 3, 'Blank_Column', '')
    
    # Reorder the columns,
    final_df = final_df[['Week_Number', 'Formatted_Date', 'SELLER_NAME', 'CATEGORY', 'app', 'rej', 'Blank_Column', 'new_col_1', 'new_col_2', 'reason']]
    
    # Modify PIM DataFrame creation to handle additional requirements
    pim_df = df[['PRODUCT_SET_SID', 'PARENTSKU']].copy()  # Use the correct column names from the input file
    pim_df.columns = ['ProductSetSid', 'ParentSKU']  # Rename columns for consistency

    # Apply mapping for 'reason' to generate 'Status' and 'Reason' columns
    pim_df['Status'] = df['reason'].apply(lambda x: 'Approved' if pd.isna(x) or x == '' else 'Rejected')
    pim_df['Reason'] = df['reason'].map(reason_mapping).fillna('Approved')  # Fill blank reasons with 'Approved'
    
    # Add Comment column
    pim_df['Comment'] = df['reason'].apply(lambda x: 'Please Use Fashion as brand name for Fashion items' if x == 'bra' else '')

    # Modify Reason column based on Status
    pim_df.loc[pim_df['Status'] == 'Approved', 'Reason'] = ''
    
    # Save the PIM DataFrame to an Excel file
    pim_output_file = f'PIM_Date_Time_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.xlsx'
    counter = 1
    while os.path.exists(os.path.join(output_folder, pim_output_file)):
        pim_output_file = f'PIM_Date_Time_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{counter}.xlsx'
        counter += 1
    
    pim_output_path = os.path.join(output_folder, pim_output_file)
    pim_df.to_excel(pim_output_path, index=False) 

    # Display success message with downloadable link for PIM file
    st.markdown(get_download_link(pim_output_path, "Download PIM File"), unsafe_allow_html=True)
    
    # Display the data from the PIM file
    st.subheader("Data from PIM File")
    st.write(pim_df)   # Add a blank

# Function to create a download link for a file
def get_download_link(file_path, text):
    with open(file_path, 'rb') as file:
        contents = file.read()
    encoded = base64.b64encode(contents).decode()
    href = f'<a href="data:file/csv;base64,{encoded}" download="{os.path.basename(file_path)}">{text}</a>'
    return href

# Streamlit app
def main():
    st.title("Excel Data Processing App")
    st.write("This app processes Excel/CSV data and generates Pivot and PIM files.")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an Excel/CSV file", type=["xls", "xlsx", "csv"])
    
    if uploaded_file is not None:
        # Display file details
        st.write("Uploaded file details:")
        file_details = {"File Name": uploaded_file.name, "File Type": uploaded_file.type, "File Size": uploaded_file.size}
        st.write(file_details)
        
        # Process the uploaded file
        if process_files(uploaded_file):
            st.stop()  # Stop the Streamlit app execution

if __name__ == "__main__":
    main()
