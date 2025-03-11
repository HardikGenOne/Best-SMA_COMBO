import pandas as pd
import numpy as np

class SMA_COMBO():
    # NOTE:-
        # please send the short_sma and long_sma as range(5,50,1)
        # otherwise it will throw error

    def __init__(self,data,short_sma,long_sma):
        self.short_sma = short_sma
        self.long_sma = long_sma
        self.data = data
    
    def getBestCombo(self):
        short_sma = self.short_sma
        long_sma = self.long_sma
        data = self.data
        result_df = pd.DataFrame(columns=["Short SMA", "Long SMA", "Total Profit (%)", "Trades Taken"])
        for sS in short_sma:
            data["SHORT_SMA"] = data["Close"].rolling(window=sS).mean()
            for lS in long_sma:
                if sS >= lS:
                    continue

                data["LONG_SMA"] = data["Close"].rolling(window=lS).mean()

                # Drop NaN rows only for this SMA combination, ensuring original data remains intact
                temp_data = data.dropna().copy()

                temp_data["SIGNAL"] = np.where(temp_data["SHORT_SMA"] > temp_data["LONG_SMA"], "BUY", "SELL")

                isBuy = False
                bought_price = 0
                result_profit = []
                count_trades = 0

                for i in range(len(temp_data["SIGNAL"])):
                    if not isBuy and temp_data["SIGNAL"].iloc[i] == "BUY":
                        isBuy = True
                        bought_price = temp_data["Close"].iloc[i]

                    elif isBuy and temp_data["SIGNAL"].iloc[i] == "SELL":
                        isBuy = False
                        sold_price = temp_data["Close"].iloc[i]
                        pnl = ((sold_price - bought_price) / bought_price) * 100
                        result_profit.append(pnl)
                        count_trades += 1

                # print(f"Short SMA: {sS}, Long SMA: {lS}, Profit: {round(sum(result_profit), 2)}, Trades Taken: {count_trades}")
                result_df = pd.concat([
                    result_df,
                    pd.DataFrame({
                        "Short SMA": [sS],
                        "Long SMA": [lS],
                        "Total Profit (%)": [round(sum(result_profit),2)],
                        "Trades Taken": [count_trades],
                        "Win Cofficient": [round(sum(result_profit),2)/count_trades]
                    })
                ],ignore_index= True)

        best_overall_return = result_df.loc[result_df["Total Profit (%)"].idxmax()]
        best_win_cofficient = result_df.loc[result_df["Win Cofficient"].idxmax()]
        print()
        print()
        print("     🔥 Best Combination 🔥")
        print("----------------------------------")
        print("!! OVERALL BEST RETURNS !! ")
        print()
        print(best_overall_return)
        print()
        print("            ---")
        print()
        print("!! OVERALL BEST WIN RATIO !! ")
        print("(Total Returns / Num Of Trades)")
        print()
        print(best_win_cofficient)

                

                
