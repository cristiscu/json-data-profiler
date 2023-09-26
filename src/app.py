"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

import json
from io import StringIO
import streamlit as st
from json_classes import JsonManager
from erd_classes import ERDManager, Theme
#import xmltodict

st.set_page_config(layout="wide")
st.title("JSON Data Profiler")

uploaded_file = st.sidebar.file_uploader(
    "Upload a JSON file", accept_multiple_files=False)

JsonManager.single_object = st.sidebar.checkbox("Single Top Array Object", value=True,
    help="Infer one single object template per array")
JsonManager.show_counts = st.sidebar.checkbox("Show Total Objects", value=True,
    help="Show the number of total objects")
JsonManager.show_samples = st.sidebar.checkbox("Show Samples", value=True,
    help="Show existing sample values")
ERDManager.show_types = st.sidebar.checkbox("Show Data Types", value=True,
    help="Show data types in the ER diagrams")
ERDManager.remove_dups = st.sidebar.checkbox("Consolidate Objects", value=False,
    help="Remove duplicate objects with similar properties, and show them once only")

JsonManager.str_truncate = st.sidebar.slider("Max Sample String Length", 1, 100, 20,
    disabled=not JsonManager.show_samples,
    help="Truncate displayed string values after a number of characters")
JsonManager.max_values = st.sidebar.slider("Max Number of Sample Values", 1, 100, 3,
    disabled=not JsonManager.show_samples,
    help="Maximum number of samples per property to display")

themes = Theme.getThemes()
theme = st.sidebar.selectbox('Theme:', tuple(themes.keys()), index=0,
    help="Color theme for the ERD")

if uploaded_file is None:
    st.write("Click on the 'Browse files' button on the sidebar to load a JSON file.")
else:
    if 'filename' not in st.session_state \
        or st.session_state.filename != uploaded_file.name:
        bytes = uploaded_file.getvalue()
        text = StringIO(bytes.decode("utf-8")).read()

        #isXml = uploaded_file.name.lower().endswith("xml")
        #if isXml: text = json.dumps(xmltodict.parse(text))

        data = json.loads(text)
        if not isinstance(data, dict) and not isinstance(data, list):
            st.error("Bad JSON Format!")
            st.stop()
        
        st.session_state['filename'] = uploaded_file.name
        st.session_state["text"] = text
        st.session_state["data"] = data
    text = st.session_state.text
    data = st.session_state.data

    tabSource, tabSchema, tabERD, tabDOT = st.tabs(
        ["Uploaded Source File", "Inferred Schema", "Inferred Object Model", "DOT Script"])

    tabSource.write("This is your uploaded JSON file. Switch to the other tabs to see the inferred schema.")
    tabSource.json(text, expanded=True)

    tabSchema.write("Here are the inferred object types for the uploaded JSON file.");
    obj = JsonManager.getTop(data, JsonManager.single_object)
    tabSchema.json(obj.dump(), expanded=True)

    tabERD.write("Here is the inferred object model for the uploaded JSON file.");
    tables = ERDManager.getTables(obj)
    chart = ERDManager.createGraph(tables, themes[theme])
    tabERD.graphviz_chart(chart, use_container_width=True)
    tabDOT.code(chart, language="dot")

