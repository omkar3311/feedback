import streamlit as st
from supabase import create_client
supabase = create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])
rows = supabase.table("java").select("*").execute().data
st.set_page_config(page_title="java")
for row in rows:
    exp_name = row["exp"]
    code_snippet = row["code"]
    with st.expander(exp_name, expanded=False):
        st.code(code_snippet, language="java")