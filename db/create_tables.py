import pandas as pd
from sqlalchemy import create_engine

credentials = {
  'host':"127.0.0.1",
  'user':"root",
  'password':"451278",
  'database':"sei"
}

engine = create_engine(f"mysql+mysqlconnector://{credentials['user']}:{credentials['password']}@{credentials['host']}/{credentials['database']}")

acts_df = pd.read_csv('data/acts.csv', sep='\t')
announcements_df = pd.read_csv('data/announcements.csv', sep='\t')

acts_df.to_sql('acts', con=engine, if_exists='fail', index=False)
announcements_df.to_sql('announcements', con=engine, if_exists='fail', index=False)


'''
To allow LOAD DATA LOCAL INFILE, you have to:

1) Edit the file /etc/mysql/mysql.conf.d/mysqld.cnf and add the following:
[mysqld]
secure-file-priv = ""

2) Restart the service
systemctl restart mysql 

3) run: $ sudo mysql -h localhost -u root sei -p
and run in mysql> $ set global local_infile=true;
'''

'''
To grand extern access to root without needing sudo, you need to:

1) Edit the file /etc/mysql/mysql.conf.d/mysqld.cnf and add the following:
[mysqld]
mysql_native_password=ON

2) Run in mysql terminal:
mysql> ALTER USER 'root'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY '<your_password>';
'''