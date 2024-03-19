import pandas as pd
import re
import os
from datetime import datetime
import streamlit as st

def check_for_color(cell_text):
    common_colors = ["navy", "black", "yellow", "red", "blue", "green", "orange", "purple", 
                     "pink", "brown", "white", "gray", "grey", "khaki", "coffee", "gold", 
                     "silver", "beige", "burgundy", "multi", "turquoise", "violet", "indigo", 
                     "maroon", "olive", "lime", "teal", "aqua", "apricot", "wine", "mocha", 
                     "multicolor", "multi", "plaid", "rose", "lily", "violet", "daisy", 
                     "tulip", "sunflower", "iris", "orchid", "lavender", "marigold", 
                     "poppy", "jasmine", "peony", "camellia", "hyacinth", "magnolia", 
                     "daffodil", "chrysanthemum", "geranium", "dahlia", "transparent", 
                     "clear", "rainbow", "caramel", "milk", "bronze", "argent", "chocolate", 
                     "stawberry", "colorful", "peach", "magenta", "carbon", "Camouflage", 
                     "camo", "stripes", "polka dot", "floral", "geometric", "animal print", 
                     "tie-dye", "chevron", "camouflage", "herringbone", "paisley", 
                     "checkered", "gingham", "tartan", "abstract", "batik", "ikat", "ombre", 
                     "checked", "cyan", "ivory", "periwinkle", "chartreuse", "fandango", 
                     "wisteria", "mauve", "vermilion", "viridian", "tangerine", "cerulean", 
                     "heliotrope", "gamboge", "xanadu", "byzantium", "caput mortuum", 
                     "persimmon", "coquelicot", "falu red", "zaffre", "wood", "mahogany", 
                     "Auburn", "turmeric", "lemon", "skin", "nude", "walnut", "copper", 
                     "chrome", "watermelon", "leopard", "lemon", "print", "tan", "Amber", 
                     "Smoky", "Smoked", "coral", "tomato", "rusty", "rust", "steel", 
                     "cream", "Champagne", "matte", "blossom", "graffiti", "sapphire",
                     "velvet", "translucent", "metal", "metallic", "iridium", "chroma", "coral",
                     "scarlet", "crimson", "ruby", "cherry", "burgundy", "vermilion", "maroon", 
                     "carmine", "raspberry", "blue", "navy", "azure", "cobalt", "cerulean", 
                     "indigo", "teal", "sky blue", "sapphire", "cyan", "green", "emerald", "lime", 
                     "olive", "jade", "mint", "sage", "forest green", "hunter green", "kelly green", 
                     "yellow", "lemon", "gold", "canary", "maize", "amber", "buttercup", "mustard", 
                     "dandelion", "honey", "orange", "tangerine", "apricot", "peach", "iron", 
                     "pumpkin", "terracotta", "rust", "salmon", "purple", "lavender", "lilac", "violet", 
                     "mauve", "plum", "grape", "amethyst", "orchid", "magenta", "pink", "blush", "rose", 
                     "bubblegum", "salmon pink", "coral pink", "fuchsia", "neon", "carnation", "peony", 
                     "brown", "chocolate", "tan", "beige", "auburn", "chestnut", "coffee", "mahogany", "sienna", 
                     "umber", "gray", "charcoal", "slate", "silver", "ash", "steel", "dove", "graphite", "pearl", 
                     "smoke", "white", "ivory", "cream", "snow", "pearl white", "off-white", "vanilla", "alabaster", 
                     "bone", "chiffon", "black", "jet", "onyx", "ebony", "charcoal black", "coal", "midnight", 
                     "obsidian", "raven", "soot"]

    if pd.isna(cell_text):
        return "No"
    
    for color in common_colors:
        if re.search(re.escape(color), cell_text, flags=re.IGNORECASE):
            return "Yes"

    return "No"

def main():
    st.title("Upload Excel Files and Process")

    uploaded_files = st.file_uploader("Upload your Excel files", type=['xlsx'], accept_multiple_files=True)

    if uploaded_files:
        # Get the directory of the current script file
        script_folder = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the file path for 'category FAS.xlsx'
        category_fas_file_path = os.path.join(script_folder, "category FAS.xlsx")

        # Check if 'category FAS.xlsx' exists in the script folder
        if os.path.isfile(category_fas_file_path):
            try:
                # Load data from 'category FAS.xlsx'
                category_fas_df = pd.read_excel(category_fas_file_path, engine='openpyxl')
            except Exception as e:
                st.error(f"Error loading 'category FAS.xlsx': {e}")
                return
        else:
            st.error("Error: File 'category FAS.xlsx' not found in the specified directory.")
            return

        try:
            # Initialize an empty DataFrame to store the combined results
            combined_df = pd.DataFrame()

            # Process each uploaded Excel file
            for uploaded_file in uploaded_files:
                try:
                    df = pd.read_excel(uploaded_file, engine='openpyxl')  # Use openpyxl engine
                    # Assuming 'COLOR' is the correct column name, adjust it if needed
                    if 'COLOR' in df.columns:
                        df['Check'] = df['COLOR'].apply(lambda x: check_for_color(str(x)))
                    
                    # Check for brand existence based on CATEGORY_CODE from category FAS.xlsx
                    if 'ID' in df.columns and 'BRAND' in df.columns:
                        df['Check_brand'] = df['ID'].apply(lambda id_value: "No"
                        if category_fas_df['CATEGORY_CODE'].isin([id_value]).any() and category_fas_df.loc[category_fas_df['CATEGORY_CODE'] == id_value, 'BRAND'].iloc[0] == "Generic":
    return "No"
else:
    return "Yes"  # Assuming if the brand is not "Generic", return "Yes"

                    
                    # Drop the column containing URLs if it exists
                    if 'URL_COLUMN_NAME' in df.columns:
                        df.drop(columns=['URL_COLUMN_NAME'], inplace=True)

                    # Concatenate the results to the combined DataFrame
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
                except Exception as e:
                    st.error(f"Error processing file '{uploaded_file.name}': {e}")

            # Get the current date and format it as 'YYYY-MM-DD'
            current_date = datetime.now().strftime('%Y-%m-%d')

            # Find a unique name for the output file
            output_file_name = f"Output_PIM_{current_date}.csv"
            output_file_path = os.path.join(script_folder, output_file_name)

            # Add a letter to the output file name if it already exists
            while os.path.exists(output_file_path):
                output_file_name = output_file_name[:-4] + chr(ord(output_file_name[-5]) + 1) + ".csv"
                output_file_path = os.path.join(script_folder, output_file_name)

            # Create the output file with the combined results and current date in CSV format with 'utf-8-sig' encoding
            combined_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

            st.success(f"Output file '{output_file_name}' created.")

            # Provide a download link for the output file
            st.download_button(
                label="Download Output File",
                data=open(output_file_path, 'rb').read(),
                file_name=output_file_name,
                mime='text/csv'
            )
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
