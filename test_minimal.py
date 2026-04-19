# test_minimal.py - MINIMAL TEST VERSION
import streamlit as st

st.set_page_config(page_title="ECHO Test", page_icon="🧠")

st.title("🧠 ECHO - Test Page")
st.write("If you can see this, Streamlit is working!")

# Test if tabs work
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    st.write("Tab 1 works!")
    if st.button("Click me"):
        st.success("Button works!")

with tab2:
    st.write("Tab 2 works!")

with tab3:
    st.write("Tab 3 works!")

st.info("If you can see all of this, the problem is with your module imports.")