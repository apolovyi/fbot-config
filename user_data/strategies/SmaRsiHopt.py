# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
import numpy as np  # noqa
import pandas as pd  # noqa
from functools import reduce
from pandas import DataFrame
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter, IStrategy, IntParameter)

# --- Custom libs here ---
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# Class should have same name as file
class SmaRsiHopt(IStrategy):
    # This strategy does not use crossovers but just enters/exits trades
    # when 'is above' / 'is under' conditions are met.

    timeframe = "30m"
    stoploss = -0.1
    minimal_roi = {
        "0": 100,
        # "0": 0.577,
        # "10832": 0.379,
        # "22671": 0.15,
        # "54827": 0
    }

    startup_candle_count = 200

    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # --- Plotting ---

    # Use this section if you want to plot the indicators on a chart after backtesting
    plot_config = {
        'main_plot': {
            # Create sma line
            'sma22': {'color': 'blue'},
            'ema50': {'color': 'green'},
            'ema200': {'color': 'purple'},
            # 'close': {'color': 'black'},
        },
        'subplots': {
            # Create rsi subplot
            "WILLR": {
                'willr': {'color': 'yellow'},
                'willr_buy_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}},
                'willr_sell_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}}
            },
            "rsi": {
                'rsi': {'color': 'orange'},
                'rsi_buy_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}},
                'rsi_sell_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}}
            },
            "MACD": {
                'macd': {'color': 'blue', 'fill_to': 'macdhist'},
                'macdsignal': {'color': 'orange'},
                'macdhist': {'type': 'bar', 'plotly': {'opacity': 0.9}}
            },
        },
    }

    # --- Define spaces for the indicators ---

    # Buy space - UNCOMMENT THIS FOR HYPEROPTING
    # rsi_buy_hline = 65
    # rsi_sell_hline = 85

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe["sma22"] = ta.SMA(dataframe, timeperiod=22)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=5)
        dataframe["rsi_buy_hline"] = 40
        dataframe["rsi_sell_hline"] = 60

        dataframe["willr_buy_hline"] = -90
        dataframe["willr_sell_hline"] = -10

        dataframe['willr'] = ta.WILLR(dataframe, timeperiod=35)

        # dataframe['wma5'] = ta.WMA(dataframe, timeperiod=5)
        # dataframe['wma50'] = ta.WMA(dataframe, timeperiod=5)
        #
        # dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['emaDelta'] = ta.EMA(dataframe, timeperiod=200)

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # print(dataframe)
        # print(metadata)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        # conditions.append(
        #     (dataframe['close'] > dataframe['sma22'])
        #     & (dataframe['rsi'] > self.rsi_buy_hline)
        # )

        conditions.append(
            (dataframe['close'] < dataframe['ema50'])
            & qtpylib.crossed_above(dataframe['macd'], dataframe['macdsignal'])
            & (dataframe['rsi'] < dataframe["rsi_buy_hline"])
            # & (dataframe['willr'] < dataframe["willr_buy_hline"])
        )

        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), 'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        conditions.append(
            (dataframe['close'] > dataframe['ema50'])
            & qtpylib.crossed_below(dataframe['macd'], dataframe['macdsignal'])
            & (dataframe['rsi'] > dataframe["rsi_sell_hline"])
            # & (dataframe['willr'] > dataframe["willr_sell_hline"])
        )

        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), 'sell'] = 1

        return dataframe
