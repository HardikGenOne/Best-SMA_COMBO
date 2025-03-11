from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

class AngleOne_Smart_API():
    def __init__(self,api_key,username,pwd,token):
        self.api_key = api_key  
        self.username = username
        self.pwd = pwd
        self.token = token
        
    def connect(self):
        api_key = self.api_key
        username = self.username
        pwd = self.pwd
        token = self.token
        smartApi = SmartConnect(api_key)
        
        try:
            token = token
            totp = pyotp.TOTP(token).now()
        except Exception as e:
            logger.error("Invalid Token: The provided token is not valid.")
            raise e

        data = smartApi.generateSession(username, pwd, totp)
        self.smartApi = smartApi
        if data['status'] == False:
            return logger.error(data)

        else:
            print("Successfully Connected 🟢") 
            # login api call
            # logger.info(f"You Credentials: {data}")
            authToken = data['data']['jwtToken']
            refreshToken = data['data']['refreshToken']
            # fetch the feedtoken
            feedToken = smartApi.getfeedToken()
            # fetch User Profile
            resources = smartApi.getProfile(refreshToken)
            smartApi.generateToken(refreshToken)
            exchange_available =resources['data']['exchanges']
            print("Got Resources and Exchange Available 🙌🏻")
            return resources,exchange_available
        
    def get_data(self,exchange,symbol,interval,fromDate,toDate):
        try:  
            token_data = self.smartApi.searchScrip(exchange, symbol)
        
            if not token_data or 'symboltoken' not in token_data["data"][0]:
                raise ValueError(f"Symbol token not found for {symbol}")

            symbol_token = token_data["data"][0]["symboltoken"]
        
        
            historicParam={
                "exchange": exchange,
                "symboltoken": symbol_token,
                "interval": interval,
                "fromdate": f"{fromDate} 09:00", 
                "todate": f"{toDate} 09:16"
            }
            hist = self.smartApi.getCandleData(historicParam)

        except Exception as e:
            logger.exception(f"Logout failed: {e}")
        
        data = pd.DataFrame(hist["data"])
        data.columns = ["Date","Open","High","Low","Close","Volume"]
        data['Date'] = pd.to_datetime(data['Date']).dt.date
    
        return data
    
    def get_FullData(self,exchange,symbol,interval,start_date):

        final_data = pd.DataFrame()
       
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        today_date = datetime.today()

        while current_date < today_date:
            
            next_date = current_date + relativedelta(months=3)
        
            end_date = min(next_date, today_date).strftime("%Y-%m-%d")

            # Fetch data for the current period
            data = self.get_data(exchange, symbol, interval, current_date.strftime("%Y-%m-%d"), end_date)
            
            # Ensure data is a DataFrame and not empty
            if isinstance(data, pd.DataFrame) and not data.empty:
                final_data = pd.concat([final_data, data], ignore_index=True)
        
            # Move to the next period
            current_date = next_date  
            time.sleep(2)
        final_data.reset_index(drop=True, inplace=True)
        return final_data
