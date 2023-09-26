"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

import json, yaml, xmltodict
from io import StringIO
import streamlit as st

from config import Config, Theme
from json_classes import JsonManager
from erd_classes import ERDManager

def loadFile():
    if 'filename' not in st.session_state \
        or st.session_state.filename != uploaded_file.name:
        bytes = uploaded_file.getvalue()
        text = StringIO(bytes.decode("utf-8")).read()

        if uploaded_file.name.lower().endswith("yml"):
            text = json.dumps(yaml.safe_load(text), indent=3)
        elif uploaded_file.name.lower().endswith("xml"):
            text = json.dumps(xmltodict.parse(text), indent=3)

        data = json.loads(text)
        if not isinstance(data, dict) and not isinstance(data, list):
            st.error("Bad Format!")
            st.stop()
        
        st.session_state['filename'] = uploaded_file.name
        st.session_state["text"] = text
        st.session_state["data"] = data

    text = st.session_state.text
    data = st.session_state.data
    return text, data

def renderFile(text, data, theme):
    tabSource, tabSchema, tabERD, tabDOT = st.tabs(
        ["Uploaded Source File", "Inferred Schema", "Inferred Object Model", "DOT Script"])

    objects = JsonManager.inferSchema(data)
    schema = objects.dump()
    ERDManager.getEntities(objects)
    chart = ERDManager.createGraph(theme)

    with tabSource:
        st.write("This is your uploaded file. Switch to the other tabs to see the inferred schema.")
        if not Config.show_json: st.code(text, language="json")
        else: st.json(text, expanded=True)

    with tabSchema:
        st.write("Here are the inferred object types for the uploaded file.");
        if not Config.show_json: st.code(schema, language="json")
        else: st.json(schema, expanded=True)

    with tabERD:
        st.write("This is your infered object model.")
        st.graphviz_chart(chart, use_container_width=True)

    with tabDOT:
        st.code(chart, language="dot")


st.set_page_config(layout="wide")
st.title("JSON Data Profiler")

uploaded_file = st.sidebar.file_uploader(
    "Upload a JSON/XML/YML file", accept_multiple_files=False)

Config.single_object = st.sidebar.checkbox("Single Top Array Object",
    value=Config.single_object,
    help="Infer one single object template per array")
Config.remove_dups = st.sidebar.checkbox("Consolidate Objects",
    value=Config.remove_dups,
    help="Remove duplicate objects with similar properties, and show them once only")
Config.show_counts = st.sidebar.checkbox("Show Total Objects",
    value=Config.show_counts,
    help="Show the number of total objects")
Config.show_samples = st.sidebar.checkbox("Show Samples",
    value=Config.show_samples,
    help="Show existing sample values")
Config.show_types = st.sidebar.checkbox("Show Data Types",
    value=Config.show_types,
    help="Show data types in the ER diagrams")
Config.show_json = st.sidebar.checkbox("Show JSON Viewer",
    value=Config.show_json,
    help="Show advanced JSON viewer or simple JSON code")

Config.max_values = st.sidebar.slider("Max Number of Sample Values",
    1, 100, Config.max_values,
    disabled=not Config.show_samples,
    help="Maximum number of samples per property to display")
Config.str_truncate = st.sidebar.slider("Max Sample String Length",
    1, 100, Config.str_truncate,
    disabled=not Config.show_samples,
    help="Truncate displayed string values after a number of characters")

themes = Theme.getThemes()
theme = st.sidebar.selectbox('Theme:', tuple(themes.keys()), index=0,
    help="Color theme for the ERD")

if uploaded_file is None:
    st.write("Click on the 'Browse files' button on the sidebar to load a file.")
else:
    text, data = loadFile()
    renderFile(text, data, themes[theme])

