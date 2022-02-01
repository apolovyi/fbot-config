# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import numpy as np
import freqtrade.vendor.qtpylib.indicators as qtpylib


class MyStrategy03_15m(IStrategy):
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 100,
        # "10": 0.379,
        # "20": 0.15,
        # "30": 0
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.3

    startup_candle_count: int = 200

    # Optimal timeframe for the strategy
    timeframe = '15m'

    # signal controls
    buy_signal_1 = False
    buy_signal_2 = True
    buy_signal_3 = True
    sell_signal_1 = False
    sell_signal_2 = True
    sell_signal_3 = True

    # trailing stoploss
    # trailing_stop = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.02

    # run "populate_indicators" only for new candle
    process_only_new_candles = False

    # Optional order type mapping
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    plot_config = {
        'main_plot': {
            'tema_s': {'color': 'blue'},
            'ema_m': {'color': 'red'},
            'ema_l': {'color': 'black'},
        },
        'subplots': {
            "rsi": {
                'rsi': {'color': 'orange'},
                'rsi_buy_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}},
                'rsi_sell_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}}
            },
            "ADX": {
                'adx': {'color': 'orange'},
                'adx_trendline': {'color': 'grey', 'plotly': {'opacity': 0.4}}
            },
        }
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        # 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144

        dataframe['rsi_buy_hline'] = 30
        dataframe['rsi_sell_hline'] = 70

        dataframe['adx_trendline'] = 17

        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=8)

        dataframe['tema_s'] = ta.TEMA(dataframe, timeperiod=8)

        dataframe['ema_m'] = ta.EMA(dataframe, timeperiod=13)
        dataframe['ema_l'] = ta.EMA(dataframe, timeperiod=55)

        dataframe['adx'] = ta.ADX(dataframe, period=5)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        if self.buy_signal_1:
            conditions = [
                dataframe["volume"] > 0,
                dataframe["adx"] >= dataframe["adx_trendline"],
                dataframe['ema_l'] >= dataframe['ema_l'].shift(1),
                qtpylib.crossed_above(dataframe['tema_s'], dataframe['ema_m']),
                # dataframe["close"] > dataframe["ema_m"],
                # dataframe["low"] < dataframe["s1_ema_xxl"],
                # dataframe["close"] > dataframe["s1_ema_xxl"],
                # qtpylib.crossed_above(dataframe["s1_ema_sm"], dataframe["s1_ema_md"]),
                # dataframe["s1_ema_xs"] < dataframe["s1_ema_xl"],
            ]
            dataframe.loc[reduce(lambda x, y: x & y, conditions), ["buy", "buy_tag"]] = (1, "buy_signal_1")

        if self.buy_signal_2:
            conditions = [
                qtpylib.crossed_above(dataframe["ema_m"], dataframe["ema_l"]),
                dataframe["volume"] > 0,
            ]
            dataframe.loc[reduce(lambda x, y: x & y, conditions), ["buy", "buy_tag"]] = (1, "buy_signal_2")

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        if self.sell_signal_1:
            conditions = [
                dataframe["volume"] > 0,
                dataframe["adx"] >= dataframe["adx_trendline"],
                qtpylib.crossed_below(dataframe['tema_s'], dataframe['ema_m']),
                dataframe["close"] > dataframe["ema_l"],
                # dataframe["low"] < dataframe["s1_ema_xxl"],
                # dataframe["close"] >= dataframe["ema_m"],
                # dataframe["close"] > dataframe["s1_ema_xxl"],
                # qtpylib.crossed_above(dataframe["s1_ema_sm"], dataframe["s1_ema_md"]),
                # dataframe["s1_ema_xs"] < dataframe["s1_ema_xl"],

            ]
            dataframe.loc[reduce(lambda x, y: x & y, conditions), ["sell", "sell_tag"]] = (1, "sell_signal_1")

        if self.sell_signal_2:
            conditions = [
                # qtpylib.crossed_below(dataframe["ema_m"], dataframe["ema_l"]),
                dataframe["volume"] < 0,
            ]
            dataframe.loc[reduce(lambda x, y: x & y, conditions), ["sell", "sell_tag"]] = (1, "sell_signal_2")

        return dataframe
