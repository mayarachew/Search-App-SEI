import streamlit as st
import mysql.connector
import toml
import pandas as pd

st.set_page_config(layout='wide', page_icon=':open_book:', page_title='Document')

st.title(':open_book:')

# Get the argument passed via URL
query_params = st.query_params

docid = query_params.get("docid", ["No argument found"])
doctype = query_params.get("doctype", ["No argument found"])

st.write(f'**Document ID: :blue[{docid}]**')

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
cursor = cnx.cursor()

raw_text = pd.read_sql(f'SELECT raw_text from {doctype} WHERE document_id = {docid};', cnx).iloc[0, 0]

st.write(raw_text)
