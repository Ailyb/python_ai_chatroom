import yfinance as yf

data = yf.download("ZC%3DF", start="2014-01-01", end="2024-12-31")
#export data to CSV

data.to_csv("C:/Users/Justin/Downloads/ZC_Futures_Data.csv")
print("Data downloaded and saved to ZC_Futures_Data.csv")