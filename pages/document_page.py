import streamlit as st
import mysql.connector
import toml
import pandas as pd

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
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Fetch raw text from the database
raw_text = pd.read_sql(f'SELECT raw_text from {doctype} WHERE document_id = {docid};', cnx).iloc[0, 0]

# Sample text for highlighting
text = 'Boletim de Atos Oficiais da XXXXXXXXX em 23/10/2024 ATO DA SECRETARIA DE TECNOLOGIA DA\
        INFORMAÇÃO Nº 8X/202X Designa servidores para atuarem como gestores e fiscais do Contrato\
        n° 5XX/202X, que fazem entre si a união, por intermédio da XXXXXXXX e do TSE. \
        XXXXXXX, 08, de novembro, de 2024, Documento assinado eletronicamente por \
        XXXXX XXXXX XXXXX XXXX XXXX, Decano(a) de Pesquisa e Inovação, em 08/01/2024, \
        às 11:59, conforme XXXXX, com fundamento na Instrução da Reitoria \
        0003/201X da XXXXX XXXXX XXXXX. A autenticidade deste documento pode ser conferida \
        no site http://XXXXX/sei/controlador_externo.php?acao=documento_conferir&id_orgao_acesso_externo=0, \
        informando o código verificador XXXXXXX e o código CRC C46CXXX. Referência: Processo nº \
        23XXX.052XXX/202X-XX SEI nº XXXXXXX.'

# Tokenize text
text = text.replace('.',' .').replace(',',' ,').replace('!',' !').replace('?',' ?').replace(':',' :').replace(';',' ;')
tokens = text.split()

# Example tags (in reality, these would come from your NER process)
# tags = '0 0 1 1 0 2 0 3 0 0 4 4 4 4 4 0 5 0 0 0 0 0 0 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0 0 0 2 0 0 2 0'
tags = '0 0 1 1 0 2 0 3 0 0 4 4 4 4 4 0 5 0 0 0 0 0 0 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0 0 0 2 0 0 2 0 6 0 3 3 3 3 3 3 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0'

tag_list = tags.split(' ')

if len(tokens) != len(tag_list):
    st.write(len(tokens))
    st.write(len(tag_list))
    raise ValueError("The number of tokens and tags must be the same.")

# Tag mappings
tags_dict = {
    '1': 'DOC',
    '2': 'ORG',
    '3': 'DAT',
    '4': 'UNI',
    '5': 'PROC',
    '6': 'LOC'
}

# Colors mapping
colors_dict = {
    '1': '#C0C0FF',  # Pastel Light Blue
    '2': '#FFCCCC',  # Pastel Light Red
    '3': '#CCFFCC',  # Pastel Light Green
    '4': '#FFCCE5',  # Pastel Light Pink
    '5': '#CCFFEB',  # Pastel Mint Green
    '6': '#FFEB3B',  # Yellow
}

# Function to generate styled legends
def show_legends(colors_dict):
    legend = ''
    for i, (tag, color) in enumerate(colors_dict.items()):
        label = tags_dict.get(tag, "Unknown")
        legend += (f'<span style="display: inline-flex; align-items: center; margin-right: 20px;">'
                f'<span style="width: 20px; height: 20px; background-color:{color}; '
                f'display: inline-block; margin-right: 10px;"></span>'
                f'<strong>{label}</strong></span>')
    return legend


# Function to highlight entities in the text
def highlight_entities(text, tag_list):
    """
    Highlight entities by wrapping them in <span> tags with background color.
    """
    highlighted_text = ""
    
    for token, tag in zip(text.split(), tag_list):  
        if tag in colors_dict:  # Ensure the token has a valid tag
            background_color = colors_dict[tag]
            hover = tags_dict.get(tag, 'UNKNOWN')  # Default to 'UNKNOWN' if tag is not found in tags_dict
            highlighted_text += f'<span style="background-color:{background_color}; padding: 2px 5px; border-radius: 4px;" class="highlighted" title="{hover}">{token}</span>'
        else:
            highlighted_text += f'{token} '  # If tag is not valid, just add the token
    
    return highlighted_text


# Show either highlighted or plain text based on checkbox state
if show_highlighted:
    # Display the highlighted text
    st.markdown(show_legends(colors_dict), unsafe_allow_html=True)
    st.markdown(highlight_entities(text, tag_list), unsafe_allow_html=True)
else:
    # Display the raw, unhighlighted text
    st.write(text)
