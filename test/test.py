print("Testing... \n")


#----------Check if the database is reachable----------#
print("Check if the database is reachable... \n")
import psycopg2
import os
#----------Database Credentials----------# 
DB_NAME=os.getenv("DB_NAME") 
DB_USER=os.getenv("DB_USER")
DB_HOST= os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_PASSWORD=os.getenv("DB_PASSWORD")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")
SPECIAL_NAME=os.getenv("SPECIAL_NAME")

#----------Connect to a database----------# 
def connection():
    con = psycopg2.connect(f"""
                           dbname={DB_NAME}
                           user={DB_USER}
                           host={DB_HOST}
                           port={DB_PORT}
                           password={DB_PASSWORD}
                           """)
    cur = con.cursor()
    return con, cur

#----------Execution----------#
if __name__ == '__main__':
    # Connection
    con = False
    try:
        con, cur = connection()
        con = True
    except:
        print("DATABASE CONNECTION: The app can't connect to the database right now. Please try again later \n")
    if con == True:
        con, cur = connection()
        print("Database Connected \n")
        
        # Close Connection
        cur.close()
        con.close()
        print("Done Checking: Successfully Close The Connection \n")
    