import pandas as pd
from fastapi import FastAPI,Query,UploadFile,File, HTTPException
from statsmodels.tsa.statespace.sarimax import SARIMAX
from database import Database
import math
import asyncio
from fastapi.middleware.cors import CORSMiddleware
database = Database()
app = FastAPI()

pivot_table_data = pd.read_csv('./pivot_table.csv')

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['*']
)

@app.on_event("startup")
async def startup():
    await database.connect()
    await database.insert_csv_data()
    # await predict_future_sales(3)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/inventory")
async def root(limit: int = 10, offset: int = 0):
    return await database.fetch_products(limit, offset)
@app.get("/all_inventory")
async def get_all_inventory(limit: int = 10, offset: int = 0):
    return await database.fetch_all_products(limit,offset)
@app.get("/all_inventory_count")
async def get_all_inventory_count():
    return await database.fetch_all_products_count()
@app.get("/inventory/{product}")
async def say_hello(product: str):
    return await database.fetch_product(product)
@app.get("/predict/{month}")
async def get_products_by_month(month: str):
    products = await database.fetch_products_by_month(month)
    return {"products": products}

@app.get("/predict/pluno/{pluno}/{month}")
async def get_prediction_by_pluno(pluno: str,month:str):
    predictions = await database.fetch_prediction_by_pluno(pluno,month)
    return {"predictions": predictions}

@app.get("/prediction/{product}")
async def fetch_prediction(product: str):
    datas = await database.fetch_prediction_product(product)
    print(datas)
    qty = 0
    if len(datas) > 0:
        for data in datas:
            qty += abs(data.get('opening_stock') - data.get('net_qty') - data.get('closing_stock'))
        qty = math.ceil(qty/len(datas))
        datas[0]['prediction'] = qty
        return datas[0]
    return {"message": "Not found"}


# @app.get("/prediction")
# async def fetch_prediction_all(year: int = Query(None, description="Year"), month: int = Query(None, description="Month")):
#     if year is None or month is None:
#         return {"message": "Please provide both year and month"}
    
#     datas = await database.fetch_all_products()
    
#     if not datas:
#         return {"message": "No data available for the specified year and month"}
    
#     qty = 0
#     for data in datas:
#         qty += abs(data.get('opening_stock') - data.get('net_qty') - data.get('closing_stock'))
#     qty = math.ceil(qty / len(datas))
#     datas[0]['prediction'] = qty
    
#     return datas[0]

# @app.post("/predict_future_sales")
# async def predict_future_sales(month: int):
#     try:
#         if month < 1 or month > 12:
#             raise ValueError("Month value must be between 1 and 12")
        
#         predictions = {}
#         for column in pivot_table_data.columns[1:]:
#             series = pivot_table_data[column]
#             predicted = await predict_product_stock(series, column, month)
#             predictions[column] = predicted
        
#         return predictions
    
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))


# async def predict_product_stock(series, column, month):
#     model_df = SARIMAX(series, order=(1, 0, 1), seasonal_order=(1, 0, 1, 12))
#     results_df = model_df.fit()
#     steps = 12
#     forecast_df = results_df.get_forecast(steps=steps)

#     # Get forecasted values and confidence intervals
#     forecast_values_df = forecast_df.predicted_mean
#     #print(forecast_values_df)
#     req_for = forecast_values_df[month-1]
#     return req_for  # Return the result instead of updating a global variable
    

#search product by name 
@app.get("/inventory/search/{name}")
async def search_product_by_name(name: str, limit: int = 10, offset: int = 0):
    return await database.search_product_by_name(name,limit,offset)
 