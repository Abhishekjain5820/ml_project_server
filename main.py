# from fastapi import FastAPI
# from database import Database
from fastapi.middleware.cors import CORSMiddleware

# database = Database()
# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],
#     allow_credentials=True,
#     allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
#     allow_headers=['*']
# )


# @app.on_event("startup")
# async def startup():
#     await database.connect()
#     await database.insert_csv_data()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()
# # @app.get("/inventory")
# # async def root():
# #     return await database.fetch_products()
# @app.get("/inventory/all")
# async def root():
#     return await database.fetch_products()
# @app.get("/inventory")
# async def root(limit: int = 10, offset: int = 0):
#     return await database.fetch_products(limit, offset)


# @app.get("/inventory/{product}")
# async def say_hello(product: str):
#     return await database.fetch_product(product)
from fastapi import FastAPI
from database import Database

database = Database()
app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()
    await database.insert_csv_data()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['*']
)

@app.get("/inventory")
async def root(limit: int = 10, offset: int = 0):
    return await database.fetch_products(limit, offset)
@app.get("/all_inventory")
async def get_all_inventory():
    return await database.fetch_all_products()
@app.get("/inventory/{product}")
async def say_hello(product: str):
    return await database.fetch_product(product)