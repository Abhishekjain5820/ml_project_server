from fastapi import FastAPI,Query,UploadFile,File, HTTPException
#from statsmodels.tsa.statespace.sarimax import SARIMAX
# from database import Database
from fastapi.middleware.cors import CORSMiddleware
import math
#import pandas as pd
# Load the trained model from the .pkl file
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
import pandas as pd
database = Database()
app = FastAPI()

# @app.post("/upload_csv/")
# async def upload_csv(file: UploadFile = File(...)):
#     contents = await file.read()
#     file_name=file.pivot_table.csv
#     df = pd.read_csv(contents)

#     return {"file_name":file_name,"file_contents": df.to_dict()}

pivot_table_data = pd.DataFrame({'./pivot_table.csv'})
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

@app.get("/prediction")
async def fetch_prediction_all(year: int = Query(None, description="Year"), month: int = Query(None, description="Month")):
    if year is None or month is None:
        return {"message": "Please provide both year and month"}
    
    datas = await database.fetch_all_products()
    
    if not datas:
        return {"message": "No data available for the specified year and month"}
    
    qty = 0
    for data in datas:
        qty += abs(data.get('opening_stock') - data.get('net_qty') - data.get('closing_stock'))
    qty = math.ceil(qty / len(datas))
    datas[0]['prediction'] = qty
    
    return datas[0]

# @app.post("/predict_future_sales/")
# async def predict_future_sales(month: str):
#     try:
#         target_month = pd.to_datetime(month)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid date format. Please provide date in YYYY-MM format.")
    
#     if target_month not in pivot_table_data['Date'].values:
#         raise HTTPException(status_code=404, detail="Data not available for the specified month.")
    
# predictions={}

# async def predict_product_stock(series,column,i):
#     model_df = SARIMAX(series, order=(1, 0, 1), seasonal_order=(1, 0, 1, 12))
#     results_df = model_df.fit()
#     steps = 12
#     forecast_df = results_df.get_forecast(steps=steps)

#     # Get forecasted values and confidence intervals
#     forecast_values_df = forecast_df.predicted_mean
#     req_for=forecast_values_df[month-1]
#     predictions.update{column:req_for}


# for column in pivot_table_data.columns[1:]:
#     product_id=column
#     series=pivot_table_data.set_index('Date')[column]
#     predicted=predict_product_stock(series,column,month)

