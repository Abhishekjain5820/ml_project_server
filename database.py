import asyncpg
from asyncpg.pool import Pool
import csv

class Database:
    def __init__(self):
        self.pool: Pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(user='postgres', password='root',database='canteen')

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    async def insert_csv_data(self):
        try:
            # Connect to PostgreSQL database
            conn = await asyncpg.connect(user='postgres',password='root', database='canteen')

            # Check if the table exists
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_name = 'canteen'
                )
            """)

            # If the table does not exist, create it
            if not table_exists:
                await conn.execute('''
                    CREATE TABLE canteen (
                        id SERIAL PRIMARY KEY,
                        month VARCHAR(256),
                        year INTEGER,
                        gp_index VARCHAR(256),
                        pluno VARCHAR(256),
                        item_name VARCHAR(256),
                        net_qty INTEGER,
                        opening_stock INTEGER,
                        closing_stock INTEGER
                    )
                ''')

                print("Table 'canteen' created successfully")

            # If the table exists, skip data insertion
            else:
                print("Table 'canteen' already exists. Skipping data insertion.")

            # If the table was created or already existed, proceed with data insertion
            if not table_exists:
                # Open the CSV file
                with open('combined_data.csv', 'r') as file:
                    reader = csv.DictReader(file)

                    # Iterate over each row in the CSV file
                    for row in reader:
                        # Extract data from the CSV row
                        month = row['Month']
                        year = int(row['Year'])
                        gp_index_no = row['GP_Index_No']
                        pluno = row['pluno']
                        item_name = row['Item_Name']
                        net_qty = int(row['Net_Qty'])
                        opening_stock = int(row['O_B'])
                        closing_stock = int(row['Closing_Stock'])

                        # Execute SQL INSERT statement
                        await conn.execute("""
                            INSERT INTO canteen (month, year, gp_index, pluno, item_name, net_qty, opening_stock, closing_stock)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """, month, year, gp_index_no, pluno, item_name, net_qty, opening_stock, closing_stock)

                print("CSV data inserted successfully")
        finally:
            # Close the database connection
            if conn:
                await conn.close()

    async def fetch_all_products(self,limit: int = 10, offset: int = 0):
        conn = None
        try:
            conn = await asyncpg.connect(user='postgres',password='root', database='canteen')
            rows = await conn.fetch("SELECT * FROM canteen WHERE net_qty>400 ORDER BY year ASC, month ASC LIMIT $1 OFFSET $2 ",limit,offset)
            data = [dict(row) for row in rows]
            return data
        finally:
            if conn:
                await conn.close()

    async def fetch_all_products_count(self):
        conn = None
        try:
            conn = await asyncpg.connect(user='postgres',password='root', database='canteen')
            rows = await conn.fetch("SELECT * FROM canteen WHERE net_qty>400 ORDER BY year ASC, month ASC")
            data = [dict(row) for row in rows]
            return data
        finally:
            if conn:
                await conn.close()


    # async def fetch_products(self, limit: int = 10, offset: int = 0):
    async def fetch_products(self, limit: int = 10, offset: int = 0):
        conn = None
        try:
            conn = await asyncpg.connect(user='postgres', password='root', database='canteen')
            
            query = "SELECT * FROM canteen LIMIT $1 OFFSET $2"
            rows = await conn.fetch(query, limit, offset)
            data = [dict(row) for row in rows]
            return data
        finally:
            if conn:
                await conn.close()
                
    # async def fetch_product(self, product_id):
    #     conn=None
    #     try:
    #         conn = await asyncpg.connect(user='postgres',password='root', database='canteen')
    #         rows = await conn.fetch("SELECT * FROM canteen WHERE pluno = $1 ORDER BY year ASC, month ASC", product_id)

    #         data = [dict(row) for row in rows]

    #         return data
    #     finally:
    #         if conn:
    #             await conn.close()
                
    async def fetch_products_by_month(self,month: str):
        month_number = month

        if month_number is None:
            raise ValueError("Invalid month name")

        conn = None
        try:
            conn = await asyncpg.connect(user='postgres', password='root', database='canteen')
            query = """
                SELECT * 
                FROM canteen 
                WHERE month = $1
                ORDER BY year ASC, month ASC,net_qty DESC
            """
            rows = await conn.fetch(query, month)
            data = []
            for row in rows:
                # Convert asyncpg.Record to dictionary
                row_dict = dict(row)
                # Calculate prediction for each row
                prediction = -1*(row_dict['opening_stock'] - (row_dict['closing_stock'] + row_dict['net_qty']))
                # Add prediction to the dictionary
                row_dict['prediction'] = prediction
                # Append modified dictionary to data list
                data.append(row_dict)
            returndata=[]
            count=0
            for row in data:
                if(row['prediction']>0  and count<10):
                    returndata.append(row)
                    count=count+1
            return returndata

        finally:
            if conn:
                await conn.close()

    async def fetch_prediction_by_pluno(self, pluno: str,month:str):
        conn = None
        # print(pluno)
        try:
            conn = await asyncpg.connect(user='postgres', password='root', database='canteen')
            query = """
                SELECT *, (-(opening_stock - (closing_stock + net_qty))) AS prediction
                FROM canteen 
                WHERE pluno = $1 and month=$2
                ORDER BY year ASC, month ASC
            """
            rows = await conn.fetch(query, pluno,month)
            print(rows)
            # data = []
            # for row in rows:
            #     # Convert asyncpg.Record to dictionary
            #     row_dict = dict(row)
            #     # Add prediction to the dictionary
            #     row_dict['prediction'] = row_dict['opening_stock'] - (row_dict['closing_stock'] + row_dict['net_qty'])
            #     # Append modified dictionary to data list
            #     data.append(row_dict)
            return rows
        finally:
            if conn:
                await conn.close()



   

    async def fetch_products_by_month(self,month: str):
        
      
        month_number = month
       
        if month_number is None:
            raise ValueError("Invalid month name")

        conn = None
        try:
            conn = await asyncpg.connect(user='postgres', password='root', database='canteen')
            rows = await conn.fetch("SELECT * FROM canteen WHERE pluno = $1 ORDER BY year ASC, month ASC", product_id)

            data = [dict(row) for row in rows]

            return data
           
        finally:
            if conn:
                await conn.close()

    async def fetch_prediction_by_pluno(self, pluno: str,month:str):
        conn = None
        print(pluno)
        try:
            conn = await asyncpg.connect(user='postgres', password='05082002', database='canteen')
            query = """
                SELECT *, (-(opening_stock - (closing_stock + net_qty))) AS prediction
                FROM canteen 
                WHERE pluno = $1 and month=$2
                ORDER BY year ASC, month ASC
            """
            rows = await conn.fetch(query, pluno,month)
            print(rows)
            # data = []
            # for row in rows:
            #     # Convert asyncpg.Record to dictionary
            #     row_dict = dict(row)
            #     # Add prediction to the dictionary
            #     row_dict['prediction'] = row_dict['opening_stock'] - (row_dict['closing_stock'] + row_dict['net_qty'])
            #     # Append modified dictionary to data list
            #     data.append(row_dict)
            return rows
        finally:
            if conn:
                await conn.close()
                

        async def fetch_product(self, product_id):
            conn=None
            try:
                conn = await asyncpg.connect(user='postgres',password='05082002', database='canteen')
                rows = await conn.fetch("SELECT * FROM canteen WHERE pluno = $1 ORDER BY year ASC, month ASC", product_id)

                data = [dict(row) for row in rows]

                return data
            finally:
                if conn:
                    await conn.close()

    async def fetch_prediction_product(self, product_id):
        conn = None
        try:
            conn = await asyncpg.connect(user='postgres',password='root', database='canteen')
            rows = await conn.fetch("SELECT * FROM canteen WHERE pluno = $1 ORDER BY year DESC, month DESC LIMIT 5", product_id)

            data = [dict(row) for row in rows]

            return data
        finally:
            if conn:
                await conn.close()  
                
    async def search_product_by_name(self, name,limit: int = 10, offset: int = 0):
        conn = None
        try:
            conn = await asyncpg.connect(user='postgres',password='root', database='canteen')
            rows = await conn.fetch("SELECT * FROM canteen WHERE item_name ILIKE $1 LIMIT $2 OFFSET $3", f"%{name}%",limit,offset)

            data = [dict(row) for row in rows]

            return data
        finally:
            if conn:
                await conn.close() 


              