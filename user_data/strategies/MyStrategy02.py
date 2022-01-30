# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class MyStrategy02(IStrategy):
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 1.9,
        # "10": 0.379,
        # "20": 0.15,
        # "30": 0
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.1

    # Optimal timeframe for the strategy
    timeframe = '1h'

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
            # 'wma12': {'color': 'red'},
            # 'wma26': {'color': 'green'},
            'ema12': {'color': 'orange'},
            'ema26': {'color': 'purple'},
            'ema200': {'color': 'black'},
            'ema100': {'color': 'red'},
            'ema150': {'color': 'green'},
        },
        'subplots': {
            "WILLR": {
                'willr': {'color': 'yellow'},
                # 'willr_buy_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}},
                # 'willr_sell_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}}
            },
            "ema_width": {
                'ema_width': {'color': 'blue'},
            }
        }
    }

    willr_buy_hline = -60
    willr_sell_hline = -30

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # dataframe['wma12'] = ta.WMA(dataframe, timeperiod=12)
        # dataframe['wma26'] = ta.WMA(dataframe, timeperiod=26)
        dataframe['ema12'] = ta.EMA(dataframe, timeperiod=10)
        dataframe['ema26'] = ta.EMA(dataframe, timeperiod=30)
        dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)
        dataframe['ema150'] = ta.EMA(dataframe, timeperiod=150)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['willr'] = ta.WILLR(dataframe, timeperiod=11)

        dataframe["ema_width"] = (
            (dataframe["ema12"] - dataframe["ema26"])
        )

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # qtpylib.crossed_above(dataframe['ema12'], dataframe['ema26']) &
                # qtpylib.crossed_above(dataframe['ema12'], dataframe['ema26']) &
                    (dataframe['willr'] < self.willr_buy_hline) &
                    (dataframe['ema_width'] < -0.01)
                # & (dataframe['ema200'] > dataframe['ema12'])
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # qtpylib.crossed_below(dataframe['ema12'], dataframe['ema26']) &
                    (dataframe['willr'] > self.willr_sell_hline) &
                    (dataframe['ema_width'] > 0.01)
                # & (dataframe['ema200'] < dataframe['ema12'])
            ),
            'sell'] = 1

        return dataframe
