'''
conda install streamlit
pip install mysql-connector-python

Install mySQL according to documentation: https://dev.mysql.com/downloads/repo/apt/
'''

import streamlit as st
import mysql.connector
import urllib.parse
import re
import toml
import pandas as pd

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
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor(buffered=True)

# Sidebar
st.sidebar.header(('About'))
st.sidebar.markdown((
    '**Search App** is an application to search for specific documents in the Electronic Information System (SEI) based on entities of the corpus.'
))

st.sidebar.header(('Documents'))

acts_docs = pd.read_sql('SELECT * from acts;', cnx)
announcements_docs = pd.read_sql('SELECT * from announcements;', cnx)

with st.sidebar.expander(('Act')):
    for _, row in acts_docs.iterrows():
        # Create a link that opens in a new tab
        document_id = str(row["document_id"])
        new_page_url = f"/document_page?doctype={urllib.parse.quote('acts')}&docid={urllib.parse.quote(document_id)}"
        st.markdown(f"""
            <a href="{new_page_url}" target="_blank"> nº {document_id}</a>
        """, unsafe_allow_html=True)


with st.sidebar.expander(('Announcement')):
    for _, row in announcements_docs.iterrows():
        # Create a link that opens in a new tab
        document_id = str(row["document_id"])
        new_page_url = f"/document_page?doctype={urllib.parse.quote('announcements')}&docid={urllib.parse.quote(document_id)}"
        st.markdown(f"""
            <a href="{new_page_url}" target="_blank"> nº {document_id}</a>
        """, unsafe_allow_html=True)


# Title
st.markdown(('## :mag: Search App'))
st.markdown(('### Find your document in SEI '))

# Form
entities_dict = {
    'Act':["Document ID","Signature","Person name","Person ID","Contract ID","Organization"],
    'Announcement':["Document ID","Signature","Person name","Organization","Subject"]
}

def callback_entities():
     st.session_state.entity = entities_dict[st.session_state["document_type"]][0]


with st.container(border=True):
    selected_type = st.selectbox(('Choose document category'), ["Act","Announcement"], key='document_type', on_change=callback_entities)
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
        'Act':'acts',
        'Announcement':'announcements',
    }
    entity_dict = {
        'Document ID': 'document_id',
        'Signature': 'person_signing',
        'Person name': 'person_name',
        'Person ID': 'person_id',
        'Contract ID': 'contract_id',
        'Organization': 'organization',
        'Subject': 'subject'
    }
    table_name = table_dict[st.session_state["document_type"]]
    entity_name = entity_dict[st.session_state["entity"]]

    df = pd.read_sql(f'SELECT * from {table_name};', cnx)

    # Search for the pattern
    pattern = rf'{st.session_state["text"]}'

    # Print results
    for _, row in df.iterrows():
        string_value = str(row[entity_name])
        match = re.search(pattern, string_value)
        if match:
            if count_finded == 0:
                st.write(f':tada: The following documents were found:')
                st.write(f'**Document ID | {st.session_state["entity"]}**')
                count_finded += 1
            document_id = str(row["document_id"])
            new_page_url = f"/document_page?doctype={urllib.parse.quote(table_name)}&docid={urllib.parse.quote(document_id)}"
            st.markdown(f"""
                <div>{count_finded}) <a href="{new_page_url}" target="_blank"> nº {document_id}</a> | {string_value}</div>
            """, unsafe_allow_html=True)
            count_finded += 1
    
    if count_finded == 0:
        st.markdown("""<div style="text-align:left;">&#128542 <b>Oh no...</b><br />No documents were found.</div>""", unsafe_allow_html=True)
        