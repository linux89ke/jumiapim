import pandas as pd
import os
from datetime import datetime
import streamlit as st
import re

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

    uploaded_file = st.file_uploader("Upload your Excel file", type=['xlsx'])
    category_file = st.file_uploader("Upload category FAS.xlsx", type=['xlsx'])

    if uploaded_file and category_file:
        try:
            # Read the uploaded file
            df = pd.read_excel(uploaded_file, engine='openpyxl')

            # Read the category file
            category_fas_df = pd.read_excel(category_file, engine='openpyxl')

            # Check if 'BRAND' column exists in the uploaded file
            if 'BRAND' in df.columns:
                # Check if any value in 'BRAND' column is 'Generic'
                if (df['BRAND'] == 'Generic').any():
                    # Check if 'CATEGORY_CODE' column exists in the category file
                    if 'CATEGORY_CODE' in category_fas_df.columns:
                        # Create a new column 'check_Brand' in the output file
                        df['check_Brand'] = df.apply(lambda row:
                            'No' if row['BRAND'] == 'Generic' and row['CATEGORY_CODE'] in category_fas_df['CATEGORY_CODE'].values else 'Yes',
                            axis=1
                        )
                    else:
                        st.error("Error: 'CATEGORY_CODE' column not found in the category file.")
                else:
                    st.error("Error: No value 'Generic' found in 'BRAND' column of the uploaded file.")
            else:
                st.error("Error: 'BRAND' column not found in the uploaded file.")

            # Now, let's check for colors
            if 'COLOR' in df.columns:
                df['Check_Color'] = df['COLOR'].apply(lambda x: check_for_color(str(x)))

            # Save the output file
            current_date = datetime.now().strftime('%Y-%m-%d')
            output_file_name = f"Output_PIM_{current_date}.csv"
            output_file_path = os.path.join(os.getcwd(), output_file_name)
            df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

            # Display success message and provide download link
            st.success(f"Output file '{output_file_name}' created.")
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
