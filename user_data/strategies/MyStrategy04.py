# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class MyStrategy04(IStrategy):
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
    stoploss = -0.05

    startup_candle_count: int = 200

    # Optimal timeframe for the strategy
    timeframe = '30m'

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
            'dema_s': {'color': 'red'},
            'tema_s': {'color': 'green'},
            'ema_s': {'color': 'orange'},
            'ema_m': {'color': 'purple'},
            'ema_l': {'color': 'black'},
        },
        'subplots': {
            "WILLR": {
                'willr': {'color': 'yellow'},
                'willr_buy_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}},
                'willr_sell_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}}
            },
            "rsi_6": {
                'rsi_6': {'color': 'orange'},
                'rsi_buy_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}},
                'rsi_sell_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}}
            },
            "rsi_15": {
                'rsi_15': {'color': 'orange'},
                'rsi_buy_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}},
                'rsi_sell_hline': {'color': 'grey', 'plotly': {'opacity': 0.4}}
            },
            "ema_width": {
                'ema_width': {'color': 'blue'},
            },
        }
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi_6'] = ta.RSI(dataframe, timeperiod=6)
        dataframe['rsi_15'] = ta.RSI(dataframe, timeperiod=10)

        dataframe['dema_s'] = ta.DEMA(dataframe, timeperiod=12)
        dataframe['tema_s'] = ta.TEMA(dataframe, timeperiod=40)

        dataframe['ema_s'] = ta.EMA(dataframe, timeperiod=6)
        dataframe['ema_m'] = ta.EMA(dataframe, timeperiod=15)
        dataframe['ema_l'] = ta.EMA(dataframe, timeperiod=100)
        dataframe['willr'] = ta.WILLR(dataframe, timeperiod=50)

        dataframe['willr_buy_hline'] = -85
        dataframe['willr_sell_hline'] = -7

        dataframe['rsi_buy_hline'] = 15
        dataframe['rsi_sell_hline'] = 85

        dataframe["ema_width"] = (
            (dataframe["ema_s"] - dataframe["ema_m"])
        )

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        conditions.append(
            # qtpylib.crossed_above(dataframe['ema12'], dataframe['ema26']) &
            # qtpylib.crossed_above(dataframe['ema_s'], dataframe['tema_s'])
            # qtpylib.crossed_below(dataframe['tema_s'], dataframe['dema_s'])
            (dataframe['rsi_6'] < dataframe['rsi_buy_hline'])
            # (dataframe['willr'] < dataframe['willr_buy_hline'])
            # & (dataframe['ema_width'] < -0.01)
            # (dataframe['ema200'] > dataframe['ema12'])
        )
        # conditions.append(
        #     (dataframe['rsi_15'] < dataframe['rsi_buy_hline'])
        #     # & (dataframe['ema_width'] < -0.01)
        #     # & (dataframe['ema200'] > dataframe['ema12'])
        # )

        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), 'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        conditions = []

        conditions.append(
            # qtpylib.crossed_below(dataframe['ema12'], dataframe['ema26']) &
            # qtpylib.crossed_above(dataframe['tema_s'], dataframe['dema_s'])
            (dataframe['rsi_6'] > dataframe['rsi_sell_hline'])
            # (dataframe['willr'] > dataframe['willr_sell_hline'])
            # & (dataframe['ema_width'] > 0.01)
            # & (dataframe['ema200'] < dataframe['ema12'])
        )
        # conditions.append(
        # (dataframe['rsi_6'] > dataframe['rsi_sell_hline'])
        #     # & (dataframe['ema_width'] < -0.01)
        #     # & (dataframe['ema200'] > dataframe['ema12'])
        # )

        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), 'sell'] = 1

        return dataframe
