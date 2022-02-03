# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class MyStrategy03_A(IStrategy):
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 0.5,
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.10

    startup_candle_count: int = 150

    # Optimal timeframe for the strategy
    timeframe = '4h'

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
            'wma_l': {'color': 'orange'},
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

        dataframe['rsi_buy_hline'] = 30
        dataframe['rsi_sell_hline'] = 75

        dataframe['adx_trendline'] = 17

        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=3)

        dataframe['tema_s'] = ta.TEMA(dataframe, timeperiod=8)
        dataframe['ema_m'] = ta.EMA(dataframe, timeperiod=34)
        dataframe['ema_l'] = ta.EMA(dataframe, timeperiod=144)
        dataframe['wma_l'] = ta.WMA(dataframe, timeperiod=89)
        dataframe['adx'] = ta.ADX(dataframe, period=21)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = [
            dataframe["volume"] > 0,
            dataframe["adx"] >= dataframe["adx_trendline"],
            dataframe["close"] < dataframe["wma_l"],
            # dataframe['ema_m'] >= dataframe['ema_m'].shift(1),
            qtpylib.crossed_above(dataframe['tema_s'], dataframe['ema_m']),
        ]
        dataframe.loc[reduce(lambda x, y: x & y, conditions), ["buy", "buy_tag"]] = (1, "buy_signal_1")

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = [
            dataframe["volume"] > 0,
            dataframe["adx"] >= dataframe["adx_trendline"],
            dataframe["close"] > dataframe["wma_l"],
            qtpylib.crossed_below(dataframe['tema_s'], dataframe['ema_m']),

        ]
        dataframe.loc[reduce(lambda x, y: x & y, conditions), ["sell", "sell_tag"]] = (1, "sell_signal_1")

        return dataframe
