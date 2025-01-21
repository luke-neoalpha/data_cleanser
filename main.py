import streamlit as st

domain_verification = st.Page("data_cleanser.py", title="Domain Verification", icon=":material/edit:")
hubspot_match = st.Page("test.py", title="Hubspot Match", icon=":material/thumb_up:")

pg = st.navigation([domain_verification, hubspot_match])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()