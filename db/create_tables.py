import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, inspect, Text
import toml


# Load database config
with open('../.streamlit/secrets.toml', 'r') as f:
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

# Read CSVs
acts = pd.read_csv('data/acts_pred.csv', sep=',')
leaves = pd.read_csv('data/leaves_pred.csv', sep=',')
resolutions = pd.read_csv('data/resolutions_pred.csv', sep=',')
std_announcements = pd.read_csv('data/std_announcements_pred.csv', sep=',')

# Define table schemas with primary keys
# metadata = MetaData()

# Table('act', metadata,
#       Column('id', Integer, primary_key=True, autoincrement=True),
#       Column('sentence', Text),
#       Column('predicted_label', Text))

# Table('leave', metadata,
#       Column('id', Integer, primary_key=True, autoincrement=True),
#       Column('sentence', Text),
#       Column('predicted_label', Text))

# Table('resolution', metadata,
#       Column('id', Integer, primary_key=True, autoincrement=True),
#       Column('sentence', Text),
#       Column('predicted_label', Text))

# Table('std_announcement', metadata,
#       Column('id', Integer, primary_key=True, autoincrement=True),
#       Column('sentence', Text),
#       Column('predicted_label', Text))

# Create all tables (with PKs)
# metadata.create_all(engine)

# Insert data
acts.to_sql('p_acts', con=engine, if_exists='replace', index=False)
leaves.to_sql('p_leaves', con=engine, if_exists='replace', index=False)
resolutions.to_sql('p_resolutions', con=engine, if_exists='replace', index=False)
std_announcements.to_sql('p_std_announcements', con=engine, if_exists='replace', index=False)

print("All tables created and data inserted.")

inspector = inspect(engine)
table_names = inspector.get_table_names()

print("Tables in the database:")
print(table_names)

# 
# '''
# To allow LOAD DATA LOCAL INFILE, you have to:

# 1) Edit the file /etc/mysql/mysql.conf.d/mysqld.cnf and add the following:
# [mysqld]
# secure-file-priv = ""

# 2) Restart the service
# systemctl restart mysql 

# 3) run: $ sudo mysql -h localhost -u root sei -p
# and run in mysql> $ set global local_infile=true;
# '''

# '''
# To grand extern access to root without needing sudo, you need to:

# 1) Edit the file /etc/mysql/mysql.conf.d/mysqld.cnf and add the following:
# [mysqld]
# mysql_native_password=ON

# 2) Run in mysql terminal:
# mysql> ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY '<your_password>';
# '''