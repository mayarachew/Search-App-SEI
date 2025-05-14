import streamlit as st
from sqlalchemy import create_engine
import toml
import pandas as pd
import ast
import hashlib
import random
import re

# Set Streamlit page config
st.set_page_config(layout='wide', page_icon=':open_book:', page_title='Document')

st.title(':open_book:')

# Get the argument passed via URL
query_params = st.query_params
docid = query_params.get("docid", ["No argument found"])
doctype = query_params.get("doctype", ["No argument found"])


st.write(f'**Document ID: :blue[{docid}]**')
show_highlighted = st.toggle("Show Highlighted Entities", value=True)


# mySQL connection setup
with open('.streamlit/secrets.toml') as f:
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

# Fetch raw text from the database
sentence = pd.read_sql(f'SELECT sentence from {doctype} WHERE id = {docid};', engine).iloc[0, 0]
labels = pd.read_sql(f'SELECT predicted_label from {doctype} WHERE id = {docid};', engine).iloc[0, 0]

sentence = ast.literal_eval(sentence)
labels = ast.literal_eval(labels)

# Form
entities_dict = {
    'p_acts':[
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
    'p_resolutions':[
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
    'p_leaves': [
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
    'p_std_announcements': [
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

entity_bio_dict = {
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

bio_to_label = {v: k for k, v in entity_bio_dict.items()}


if len(sentence) != len(labels):
    st.write(len(sentence))
    st.write(len(labels))
    raise ValueError("The number of tokens and tags must be the same.")

def generate_light_hex_color(label):
    """Generate a consistent light hex color based on a string label."""
    # Hash the label and use it to seed color values
    hash_digest = hashlib.md5(label.encode()).hexdigest()
    
    # Use chunks of the hash to generate RGB values in a light range (160–220)
    r = 160 + int(hash_digest[0:2], 16) % 61
    g = 160 + int(hash_digest[2:4], 16) % 61
    b = 160 + int(hash_digest[4:6], 16) % 61

    return f'#{r:02x}{g:02x}{b:02x}'

# Collect all unique entities
all_entities = set()
for entity_list in entities_dict.values():
    all_entities.update(entity_list)

# Assign a light hex color to each unique entity
entity_color_map = {entity: generate_light_hex_color(entity) for entity in sorted(all_entities)}


def show_legends(entity_color_map):
    legend = ''
    for entity_label, color in entity_color_map.items():
        label = entity_label
        legend += (
            f'<span style="display: inline-flex; align-items: center; margin-right: 20px;">'
            f'<span style="width: 20px; height: 20px; background-color:{color}; '
            f'display: inline-block; margin-right: 10px; border-radius: 3px; border: 1px solid #ccc;"></span>'
            f'<strong>{label}</strong></span>'
        )
    return legend



def highlight_entities(text, tag_list):
    """
    Highlight entities using consistent colors from entity_color_map.
    """
    highlighted_text = ""

    for token, label in zip(text, labels):
        match = re.match(r'^[BI]-(.+)', label)  # Match B-ORG, I-DAT, etc.
        if match:
            entity_code = match.group(1)  # e.g., "ORG"
            bio_label = bio_to_label.get(entity_code, entity_code)  # e.g., "Organization"
            color = entity_color_map.get(bio_label, "#cccccc")
            highlighted_text += (
                f'<span style="background-color:{color}; padding: 1px 8px; '
                f'border-radius: 4px; margin: -3px;" title="{bio_label}">'
                f'{token}</span> '
            )
        else:
            highlighted_text += f'{token} '

    return highlighted_text.strip()



# Show either highlighted or plain text based on checkbox state
if show_highlighted:
    # Display the highlighted text
    st.markdown(show_legends(entity_color_map), unsafe_allow_html=True)
    st.markdown(highlight_entities(sentence, labels), unsafe_allow_html=True)
else:
    # Display the raw, unhighlighted text
    st.write(' '.join(sentence))
