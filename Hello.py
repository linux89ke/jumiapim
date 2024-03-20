import streamlit as st

# Set page title and favicon
st.set_page_config(page_title="Welcome to My Jumia App", page_icon=":wave:")

# Custom CSS to change the background color
st.markdown(
    """
    <style>
    .stApp {
        background-color: orange;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header
st.title("Welcome to My Jumia App!")
st.markdown("This is my work app")

# Description
st.write("""
## About This App
This app is designed to [briefly describe the purpose of your app]. It provides [list some key features or functionalities]. 

Feel free to explore and interact with the different components!
""")
