# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import numpy as np
import pandas as pd
import freqtrade.vendor.qtpylib.indicators as qtpylib


class MyStrategy03_15m(IStrategy):
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 0.25,
        "10": 0.379,
        "20": 0.15,
        # "60": 0
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.3

    startup_candle_count: int = 200

    # Optimal timeframe for the strategy
    timeframe = '15m'

    # signal controls
    buy_signal_1 = True
    buy_signal_2 = True
    buy_signal_3 = True
    sell_signal_1 = True
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
            'smooth_ha_o': {'color': 'pink'},
            # 'tema_s': {'color': 'red'},
            # 'ema_s': {'color': 'violet'},
            'ema_m': {'color': 'blue'},
            # 's3': {'color': 'green'},
            # 'r3': {'color': 'orange'},
            'smooth_ha_c': {'color': 'black'},
            'ema_low': {
                'color': 'green',  # optional
                'fill_to': 'ema_high',
                # 'fill_label': 'Ichimoku Cloud',  # optional
                'fill_color': 'rgba(255,76,46,0.2)',  # optional
            },
            # plot senkou_b, too. Not only the area to it.
            'ema_high': {}
        },
        'subplots': {
            "RSI": {
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

        # dataframe['hl'] = dataframe['low'].rolling(21).min()
        # dataframe['hh'] = dataframe['high'].rolling(21).max()
        # dataframe = pivots_points(dataframe)
        # print(dataframe)

        dataframe['rsi_buy_hline'] = 30
        dataframe['rsi_sell_hline'] = 75

        dataframe['adx_trendline'] = 20

        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=3)

        dataframe['tema_s'] = ta.EMA(dataframe, timeperiod=89)
        dataframe['ema_s'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema_m'] = ta.EMA(dataframe, timeperiod=34)

        dataframe['ema_low'] = ta.EMA(dataframe["low"], timeperiod=5)
        dataframe['ema_high'] = ta.EMA(dataframe["high"], timeperiod=5)
        dataframe['ema_l'] = ta.EMA(dataframe, timeperiod=89)

        dataframe['adx'] = ta.ADX(dataframe, period=3)

        dataframe = HA(dataframe, 4)

        # # # Heikin Ashi Strategy
        # heikinashi = qtpylib.heikinashi(dataframe)
        # dataframe['ha_open'] = heikinashi['open']
        # dataframe['ha_close'] = heikinashi['close']
        # dataframe['ha_high'] = heikinashi['high']
        # dataframe['ha_low'] = heikinashi['low']
        #
        # dataframe['ha_green'] = dataframe['ha_open'] < dataframe['ha_close']
        # dataframe['ha_red'] = dataframe['ha_open'] > dataframe['ha_close']

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        if self.buy_signal_1:
            conditions = [
                dataframe["volume"] > 0,
                dataframe["close"] > dataframe["ema_m"],
                dataframe["adx"] > dataframe["adx_trendline"],
                dataframe["rsi"] < dataframe["rsi_buy_hline"],
                # dataframe['ha_open'] < dataframe['ha_close']
                # dataframe["close"] >= dataframe["hh"].shift(1),
                # qtpylib.crossed_above(dataframe['ema_s'], dataframe['ema_m']),
                # qtpylib.crossed_above(dataframe['ha_close'], dataframe['ema_high']),
                # dataframe["close"] > dataframe["ema_m"],
                # dataframe["low"] < dataframe["s1_ema_xxl"],
                # dataframe["close"] > dataframe["s1_ema_xxl"],
                # qtpylib.crossed_above(dataframe["s1_ema_sm"], dataframe["s1_ema_md"]),
                # dataframe["s1_ema_xs"] < dataframe["s1_ema_xl"],
            ]
            dataframe.loc[reduce(lambda x, y: x & y, conditions), ["buy", "buy_tag"]] = (1, "buy_signal_1")

        # if self.buy_signal_2:
        #     conditions = [
        #         qtpylib.crossed_above(dataframe["ema_m"], dataframe["ema_l"]),
        #         dataframe["volume"] > 0,
        #     ]
        #     dataframe.loc[reduce(lambda x, y: x & y, conditions), ["buy", "buy_tag"]] = (1, "buy_signal_2")

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        if self.sell_signal_1:
            conditions = [
                dataframe["volume"] < 0,
                # dataframe["close"] > dataframe["ema_m"],
                # dataframe["adx"] > dataframe["adx_trendline"],
                # dataframe["rsi"] < dataframe["rsi_buy_hline"],
                # qtpylib.crossed_below(dataframe['ha_open'], dataframe['ema_low']),
                # qtpylib.crossed_below(dataframe['ema_s'], dataframe['ema_m']),
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


## smoothed Heiken Ashi
def HA(dataframe, smoothing=None):
    df = dataframe.copy()

    df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4

    df.reset_index(inplace=True)

    ha_open = [(df['open'][0] + df['close'][0]) / 2]
    [ha_open.append((ha_open[i] + df['HA_Close'].values[i]) / 2) for i in range(0, len(df) - 1)]
    df['HA_Open'] = ha_open

    df.set_index('index', inplace=True)

    df['HA_High'] = df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
    df['HA_Low'] = df[['HA_Open', 'HA_Close', 'low']].min(axis=1)

    if smoothing is not None:
        sml = abs(int(smoothing))
        if sml > 0:
            df['smooth_ha_o'] = ta.EMA(df['HA_Open'], sml)
            df['smooth_ha_c'] = ta.EMA(df['HA_Close'], sml)
            df['smooth_ha_h'] = ta.EMA(df['HA_High'], sml)
            df['smooth_ha_l'] = ta.EMA(df['HA_Low'], sml)

    return df
