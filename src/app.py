"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

import json, yaml, xmltodict, urllib.parse
from io import StringIO
import streamlit as st

from config import Config
from json_classes import JsonManager
from erd_classes import ERDManager

def loadFile():
    filename = "test.json" if uploaded_file is None else uploaded_file.name
    filename = filename.lower()
    if 'filename' not in st.session_state \
        or st.session_state.filename != filename:
        if uploaded_file is not None:
            bytes = uploaded_file.getvalue()
            raw = StringIO(bytes.decode("utf-8")).read()
        else:
            with open(filename) as f:
                raw = f.read()

        if filename.endswith(".yml") or filename.endswith(".yaml"):
            text = json.dumps(yaml.safe_load(raw), indent=3)
            filetype = "yaml"
        elif filename.endswith(".xml"):
            text = json.dumps(xmltodict.parse(raw), indent=3)
            filetype = "xmlDoc"
        else:
            text = raw
            filetype = "json"

        data = json.loads(text)
        if not isinstance(data, dict) and not isinstance(data, list):
            st.error("Bad Format!")
            st.stop()
        
        st.session_state['filename'] = filename
        st.session_state['filetype'] = filetype
        st.session_state["raw"] = raw
        st.session_state["text"] = text
        st.session_state["data"] = data

    filetype = st.session_state.filetype
    raw = st.session_state.raw
    text = st.session_state.text
    data = st.session_state.data
    return raw, text, data

def renderFile():
    raw, text, data = loadFile()
    objects = JsonManager.inferSchema(data)
    schema = objects.dump()
    ERDManager.getEntities(objects)
    chart = ERDManager.createGraph()

    if st.session_state.filetype != "json":
        tabRowName = "YAML Source File" if st.session_state.filetype == "yaml" else "XML Source File"
        tabRaw, tabSource, tabSchema, tabERD, tabDOT = st.tabs(
            [tabRowName, "Converted to JSON Source File", "Inferred Schema", "Inferred Object Model", "Generated Script"])

        with tabRaw:
            st.caption("This is your raw uploaded file. Switch to the other tabs to see the inferred schema.")
            st.code(raw, language=st.session_state.filetype, line_numbers=Config.show_line_numbers)
    else:
        tabSource, tabSchema, tabERD, tabDOT = st.tabs(
            ["JSON Source File", "Inferred Schema", "Inferred Object Model", "Generated Script"])

    with tabSource:
        st.caption("This is your eventually converted and formatted source file, in JSON.")
        if not Config.show_json:
            st.code(text, language="json", line_numbers=Config.show_line_numbers)
        else:
            st.json(text, expanded=True)

    with tabSchema:
        st.caption("Here are the inferred object types for the uploaded file, in JSON.");
        if not Config.show_json:
            st.code(schema, language="json", line_numbers=Config.show_line_numbers)
        else:
            st.json(schema, expanded=True)

    with tabERD:
        st.caption("This is your infered object model, with GraphViz.")
        st.graphviz_chart(chart, use_container_width=True)

    with tabDOT:
        st.caption("This is the DOT script generated for your previous GraphViz infered object model.")
        link = f'http://magjac.com/graphviz-visual-editor/?dot={urllib.parse.quote(chart)}'
        st.link_button("Test this online!", link)
        st.code(chart, language="dot", line_numbers=Config.show_line_numbers)


st.set_page_config(layout="wide")
st.title("JSON Data Profiler")
st.caption("Upload a JSON, YAML or XML data file, and get its inferred schema and a Entity-Relationship diagram.")

uploaded_file = st.sidebar.file_uploader(
    "Upload a JSON, XML, or YML file", accept_multiple_files=False)

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
Config.show_line_numbers = st.sidebar.checkbox("Show Line Numbers",
    value=Config.show_line_numbers,
    help="Show line numbers when displaying raw JSON, XML, YAML or DOT code")
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

Config.loadThemes()
themeName = st.sidebar.selectbox('Theme:', tuple(Config.themes.keys()), index=0,
    help="Color theme for the ERD")
Config.theme = Config.themes[themeName]

#if uploaded_file is None:
#    st.write("Click on the 'Browse files' button on the sidebar to load a file.")
#else:
renderFile()
