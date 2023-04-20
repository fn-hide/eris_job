from sqlalchemy import create_engine



class Connection:
    def __init__(self, username, password, host, port, db_name):
        self.engine = create_engine(
            url=f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}?driver=SQL Server",
        )
    
    def connect(self):
        return self.engine.connect()
    


if __name__ == '__main__':
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    connection = database.connect()

    tables = database.engine.table_names()
    print(tables)

