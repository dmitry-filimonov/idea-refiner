import sys

import streamlit as st
from streamlit.web import cli as stcli
from st_pages import Page, show_pages


def main():
    st.title("Idea Refiner")
    st.text("Please select page")

    show_pages(
        [
            Page("streamlit_pages/refiner.py", "Refiner", "🙌"),
        ]
    )


if __name__ == '__main__':
    if st.runtime.exists():
        main()
    else:
        sys.argv = ['streamlit', 'run', sys.argv[0]]
        sys.exit(stcli.main())
