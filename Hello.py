import streamlit as st

# Set page title and favicon
st.set_page_config(page_title="Welcome to My Jumia App", page_icon=":wave:")

# Header
st.title("Welcome to My Jumia App!")
st.markdown("This is my work app")

# Description
st.write("""
## About This App
This app is designed to [briefly describe the purpose of your app]. It provides [list some key features or functionalities]. 

Feel free to explore and interact with the different components!

## How to Use
To use this app, simply follow these steps:
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Get Started
Ready to dive in? Let's start by selecting an option from the sidebar menu on the left.
""")
