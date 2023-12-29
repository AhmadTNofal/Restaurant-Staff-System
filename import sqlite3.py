import mysql.connector
from mysql.connector import Error

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def generate_table_id(branch_id, table_number):
    return f"{branch_id}-T{str(table_number).zfill(2)}"

def create_tables_auto(connection):
    cursor = connection.cursor()
    select_branches_query = "SELECT BranchID, NumberOfTables FROM Branch"
    cursor.execute(select_branches_query)
    branches = cursor.fetchall()

    for branch_id, number_of_tables in branches:
        for table_number in range(1, number_of_tables + 1):
            table_id = generate_table_id(branch_id, table_number)
            create_table_entry = "INSERT INTO Tables (TableID, BranchID) VALUES (%s, %s)"
            cursor.execute(create_table_entry, (table_id, branch_id))
    
    connection.commit()
    print("Tables created successfully")
    cursor.close()

def main():
    # Replace 'host_name', 'user_name', 'user_password', 'db_name' with your MySQL credentials and database name.
    connection = create_connection('mysqldevoyard.mysql.database.azure.com', 'admintest', 'P@ssw0rd', 'group1_asd')

    # Function to automatically generate table entries
    create_tables_auto(connection)

    # Close the connection
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")

if __name__ == "__main__":
    main()
