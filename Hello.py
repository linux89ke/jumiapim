import pandas as pd
from datetime import datetime
import os
import streamlit as st

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
    
    # Read the Excel file into a DataFrame
    df = pd.read_excel(input_file)
    
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
        'col': 'Wrong Color',
        'cat': 'Wrong Category',
        'var': 'Wrong Variation - Size Only',
        'bra': 'Wrong Brand',
        'Wrong Variation - means size only': 'Wrong Variation - means size only'
    }
    
    # Update the reason mapping as per your requirement
    reason_mapping.update({'col': 'Wrong Color'})
    
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
    
    # Reorder the columns, placing 'reason' at the end
    final_df = final_df[['Week_Number', 'Formatted_Date', 'SELLER_NAME', 'CATEGORY', 'app', 'rej', 'Blank_Column', 'new_col_1', 'new_col_2', 'reason']]
    
    # Save the Pivot DataFrame to a CSV file
    pivot_output_path = os.path.join(output_folder, pivot_output_file)
    final_df.to_csv(pivot_output_path, index=False)
    st.success(f"Pivot formatted data has been created and saved to [{pivot_output_path}]({pivot_output_path})")
    
    # Define the base output file name for PIM file
    pim_output_file = f'PIM_Date_Time_{datetime.now().strftime("%Y-%m-%d_%H-%M")}.csv'
    counter = 1
    while os.path.exists(os.path.join(output_folder, pim_output_file)):
        pim_output_file = f'PIM_Date_Time_{datetime.now().strftime("%Y-%m-%d_%H-%M")}_{counter}.csv'
        counter += 1
    
    # Create the PIM DataFrame
    pim_df = df[['PRODUCT_SET_SID', 'PARENTSKU']].copy()  # Use the correct column names from the input file
    pim_df.columns = ['ProductSetSid', 'ParentSKU']  # Rename columns for consistency
    
    # Apply mapping for 'reason' to generate 'Status' and 'Reason' columns
    pim_df['Status'] = df['reason'].apply(lambda x: 'Approved' if pd.isna(x) or x == '' else 'Rejected')
    pim_df['Reason'] = df['reason'].map(reason_mapping).fillna('Approved')  # Fill blank reasons with 'Approved'
    pim_df.loc[pim_df['Status'] == 'Approved', ['Reason', 'Comment']] = ''
    
    # Apply specific mappings for certain reasons
    pim_df.loc[pim_df['Reason'] == 'Wrong Brand', 'Comment'] = 'Please use Fashion as brand name'
    
    # Sort PIM DataFrame by 'Status'
    pim_df.sort_values(by='Status', ascending=False, inplace=True)
    
    # Save the PIM DataFrame to a CSV file
    pim_output_path = os.path.join(output_folder, pim_output_file)
    pim_df.to_csv(pim_output_path, index=False)
    st.success(f"PIM formatted data has been created and saved to [{pim_output_path}]({pim_output_path})")

# Streamlit app
def main():
    st.title("Excel Data Processing App")
    st.write("This app processes Excel data and generates Pivot and PIM files.")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])
    
    if uploaded_file is not None:
        # Display file details
        st.write("Uploaded file details:")
        file_details = {"File Name": uploaded_file.name, "File Type": uploaded_file.type, "File Size": uploaded_file.size}
        st.write(file_details)
        
        # Process the uploaded file
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            process_files(uploaded_file)
            progress_bar.progress(percent_complete + 1)

if __name__ == "__main__":
    main()

