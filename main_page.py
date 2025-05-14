'''
conda install streamlit
pip install mysql-connector-python

Install mySQL according to documentation: https://dev.mysql.com/downloads/repo/apt/
'''

import streamlit as st
import urllib.parse
import re
import toml
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, inspect, Text
import ast

# Page configs
st.set_page_config(layout='wide', page_icon=':mag:', page_title='Search App')

# mySQL connection
with open('.streamlit/secrets.toml', 'r') as f:
    config = toml.load(f)

config = {
    'user': config['connections']['mysql']['username'],
    'password': config['connections']['mysql']['password'],
    'host': config['connections']['mysql']['host'],
    'database': config['connections']['mysql']['database'],
    'port': config['connections']['mysql']['port']
}

# Create engine
engine = create_engine(
    f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset=utf8mb4"
)
# Sidebar
st.sidebar.header(('About'))
st.sidebar.markdown((
    '**SEI Search App** is a prototype application designed to search for specific documents in the Electronic Information System (SEI) based on entities extracted from the SEI corpus.'
))

st.sidebar.header(('Documents'))

act_docs = pd.read_sql('SELECT * from p_acts;', engine)
leave_docs = pd.read_sql('SELECT * from p_leaves;', engine)
resolution_docs = pd.read_sql('SELECT * from p_resolutions;', engine)
std_announcement_docs = pd.read_sql('SELECT * from p_std_announcements;', engine)

with st.sidebar.expander(('Act')):
    for _, row in act_docs.iterrows():
        # Create a link that opens in a new tab
        document_id = str(row["id"])
        new_page_url = f"/document_page?doctype={urllib.parse.quote('p_acts')}&docid={urllib.parse.quote(document_id)}"
        st.markdown(f"""
            <a href="{new_page_url}" target="_blank"> nº {document_id}</a>
        """, unsafe_allow_html=True)

with st.sidebar.expander(('Leave')):
    for _, row in leave_docs.iterrows():
        # Create a link that opens in a new tab
        document_id = str(row["id"])
        new_page_url = f"/document_page?doctype={urllib.parse.quote('p_leaves')}&docid={urllib.parse.quote(document_id)}"
        st.markdown(f"""
            <a href="{new_page_url}" target="_blank"> nº {document_id}</a>
        """, unsafe_allow_html=True)

with st.sidebar.expander(('Resolution')):
    for _, row in resolution_docs.iterrows():
        # Create a link that opens in a new tab
        document_id = str(row["id"])
        new_page_url = f"/document_page?doctype={urllib.parse.quote('p_resolutions')}&docid={urllib.parse.quote(document_id)}"
        st.markdown(f"""
            <a href="{new_page_url}" target="_blank"> nº {document_id}</a>
        """, unsafe_allow_html=True)

with st.sidebar.expander(('Standard Announcement')):
    for _, row in std_announcement_docs.iterrows():
        # Create a link that opens in a new tab
        document_id = str(row["id"])
        new_page_url = f"/document_page?doctype={urllib.parse.quote('p_std_announcements')}&docid={urllib.parse.quote(document_id)}"
        st.markdown(f"""
            <a href="{new_page_url}" target="_blank"> nº {document_id}</a>
        """, unsafe_allow_html=True)

entity_dict = {
        'Location': 'LOC',
        'SEI\'s Process Number': 'SEI',
        'Motive': 'MOT',
        'DOU information': 'DOU',
        'Enrollment number': 'MAT',
        'Subject': 'SUB',
        'Begin Date': 'BDT',
        'Regulation or Article number': 'ART',
        'End Date': 'EDT',
        'Cost': 'ONU',
        'Person\'s Name': 'PER',
        'Organization': 'ORG',
        'University related': 'UNI',
        'Position': 'POS',
        'Date': 'DAT',
        'Object': 'OBJ',
        'Document Number': 'NUM',
        'Correct Information': 'COR',
        'Address of Announcement': 'URL',
        'Wrong Information': 'WRG',
        'Type': 'TYP',
        'Meeting Number': 'MET',
    }

# Title
st.markdown(('## :mag: SEI Search App'))
st.markdown(('### Find your document in SEI '))

# Form
entities_dict = {
    'Act':[
        "SEI\'s Process Number", 
        "Organization", 
        "Person's Name", 
        "Location", 
        "Date", 
        "Begin Date", 
        "End Date", 
        "Document Number", 
        "Enrollment number", 
        "Subject", 
        "University related", 
        "Object", 
        "Position", 
        "Regulation or Article number", 
        "DOU information"],
    'Resolution':[
        "SEI's Process Number",
        "Organization",
        "Person\'s Name",
        "Document Number",
        "Subject",
        "University related",
        "Date",
        "Meeting Number",
        "Object",
        "Position",
        "Regulation or Article number"],
    'Leave': [
        "SEI's Process Number",
        "Location",
        "Organization",
        "Person's Name",
        "Document Number",
        "Begin Date",
        "End Date",
        "Enrollment number",
        "Subject",
        "University related",
        "Cost",
        "Position",
        "DOU information",
        "Justification"],
    'Standard Announcement': [
        "SEI's Process Number",
        "Organization",
        "Person's Name",
        "Position",
        "Date",
        "Address of Announcement",
        "Type",
        "Document Number",
        "Wrong Information",
        "Correct Information",
        "Subject",
        "University related",
        "Object",
        "Regulation or Article number"
    ]
}

def callback_entities():
     st.session_state.entity = entities_dict[st.session_state["document_type"]][0]


with st.container(border=True):
    selected_type = st.selectbox(('Choose document category'), ["Act","Leave","Resolution","Standard Announcement"], key='document_type', on_change=callback_entities)
    col1, col2 = st.columns(2)
    with col1:
        selected_entity = st.selectbox(('Choose entities'), entities_dict[selected_type], key='entity')
    with col2:
        input_text = st.text_input('Text to be searched', key='text')

    submit_button = st.button(label='Search')


# Display content
if submit_button:
    count_finded = 0

    # Perform query
    table_dict= {
        'Act':'p_acts',
        'Leave':'p_leaves',
        'Resolution':'p_resolutions',
        'Standard Announcement':'p_std_announcements'
    }
    
    table_name = table_dict[st.session_state["document_type"]]
    entity_name = entity_dict[st.session_state["entity"]]

    df = pd.read_sql(f'SELECT * from {table_name};', engine)

    # Search for the pattern
    search_term = rf'{st.session_state["text"]}'

    # Print results
    for _, row in df.iterrows():
        sentence = ast.literal_eval(row['sentence'])
        labels = ast.literal_eval(row['predicted_label'])

        words_from_entity = [word for word, label in zip(sentence, labels) if entity_name in label]
        joined_text = ' '.join(words_from_entity)

        match = re.search(rf'\b({re.escape(search_term)})\b', joined_text, flags=re.IGNORECASE)

        if match:
            matched_word = match.group(1)
            if count_finded == 0:
                st.write(f':tada: The following documents were found:')
                st.write(f'**Document ID | {st.session_state["entity"]}**')
                count_finded += 1
            document_id = str(row["id"])
            new_page_url = f"/document_page?doctype={urllib.parse.quote(table_name)}&docid={urllib.parse.quote(document_id)}"
            st.markdown(f"""
                <div>{count_finded}) <a href="{new_page_url}" target="_blank"> nº {document_id}</a> | {matched_word}</div>
            """, unsafe_allow_html=True)
            count_finded += 1
    
    if count_finded == 0:
        st.markdown("""<div style="text-align:left;">&#128542 <b>Oh no...</b><br />No documents were found.</div>""", unsafe_allow_html=True)
        