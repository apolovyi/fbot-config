# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta
import numpy as np
import freqtrade.vendor.qtpylib.indicators as qtpylib


class MyStrategy05(IStrategy):
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "0": 11.9,
        # "10": 0.379,
        # "20": 0.15,
        # "30": 0
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.05

    startup_candle_count: int = 200

    # Optimal timeframe for the strategy
    timeframe = '4h'

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
            'dema_s': {'color': 'purple'},
            'tema_s': {'color': 'blue'},
            'ema_s': {'color': 'orange'},
            'ema_m': {'color': 'red'},
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
            "fisher_rsi_norma": {
                'fisher_rsi_norma': {'color': 'orange'},
            },
            "ADX": {
                'adx': {'color': 'orange'},
            },
            "ema_width": {
                'ema_width': {'color': 'blue'},
            },
            "rmi": {
                'rmi': {'color': 'blue'},
            },
            "rmi_up": {
                'rmi_up': {'type': 'bar', 'plotly': {'opacity': 0.9}}
            },
            "rmi_up_trend": {
                'rmi_up_trend': {'type': 'bar', 'plotly': {'opacity': 0.9}}
            },
            "rmi_up-2": {
                'rmi_up': {}
            },
        }
    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi_6'] = ta.RSI(dataframe, timeperiod=13)
        dataframe['rsi_15'] = ta.RSI(dataframe, timeperiod=15)

        dataframe['dema_s'] = ta.DEMA(dataframe, timeperiod=21)
        dataframe['tema_s'] = ta.TEMA(dataframe, timeperiod=13)

        dataframe['ema_s'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema_m'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['ema_l'] = ta.EMA(dataframe, timeperiod=89)
        dataframe['willr'] = ta.WILLR(dataframe, timeperiod=89)

        dataframe['willr_buy_hline'] = -85
        dataframe['willr_sell_hline'] = -7

        dataframe['rsi_buy_hline'] = 15
        dataframe['rsi_sell_hline'] = 85

        dataframe['adx_trendline'] = 30

        dataframe["ema_width"] = (
            (dataframe["ema_s"] - dataframe["ema_m"])
        )

        # dmi = fta.DMI(dataframe, period=14)
        # dataframe['dmi_plus'] = dmi['DI+']
        # dataframe['dmi_minus'] = dmi['DI-']
        dataframe['adx'] = ta.ADX(dataframe, period=5)

        dataframe['rmi'] = RMI(dataframe, length=13, mom=5)

        dataframe['rmi_up'] = np.where(dataframe['rmi'] >= dataframe['rmi'].shift(), 1, 0)
        dataframe['rmi_up_trend'] = np.where(dataframe['rmi_up'].rolling(5).sum() >= 3, 1, 0)

        # dataframe = HA(dataframe, 4)

        # # Chart type
        # # ------------------------------------
        # # Heikin Ashi Strategy
        heikinashi = qtpylib.heikinashi(dataframe)
        dataframe['ha_open'] = heikinashi['open']
        dataframe['ha_close'] = heikinashi['close']
        dataframe['ha_high'] = heikinashi['high']
        dataframe['ha_low'] = heikinashi['low']

        # RSI
        # dataframe['rsi'] = ta.RSI(dataframe, timeperiod=21)

        # Inverse Fisher transform on RSI, values [-1.0, 1.0] (https://goo.gl/2JGGoy)
        rsi = 0.1 * (dataframe['rsi_15'] - 50)
        dataframe['fisher_rsi'] = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)
        # Inverse Fisher transform on RSI normalized, value [0.0, 100.0] (https://goo.gl/2JGGoy)
        dataframe['fisher_rsi_norma'] = 50 * (dataframe['fisher_rsi'] + 1)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        if self.buy_signal_1:
            conditions = [
                dataframe["adx"] < dataframe["adx_trendline"],
                dataframe["close"] < dataframe["ema_m"],
                dataframe["close"] > dataframe["ema_l"],
                # qtpylib.crossed_above(dataframe['dema_s'], dataframe['tema_s']),
                qtpylib.crossed_above(dataframe['ema_s'], dataframe['dema_s']),
                # dataframe["low"] < dataframe["s1_ema_xxl"],
                # dataframe["close"] > dataframe["s1_ema_xxl"],
                # qtpylib.crossed_above(dataframe["s1_ema_sm"], dataframe["s1_ema_md"]),
                # dataframe["s1_ema_xs"] < dataframe["s1_ema_xl"],
                dataframe["volume"] > 0,
            ]
            dataframe.loc[reduce(lambda x, y: x & y, conditions), ["buy", "buy_tag"]] = (1, "buy_signal_1")

        if self.buy_signal_2:
            conditions = [
                qtpylib.crossed_above(dataframe["ema_m"], dataframe["ema_l"]),
                # dataframe["close"] < dataframe["ema_s"],
                dataframe["volume"] > 0,
            ]
            dataframe.loc[reduce(lambda x, y: x & y, conditions), ["buy", "buy_tag"]] = (1, "buy_signal_2")

        # conditions.append(
        #     (#
        #     qtpylib.crossed_above(dataframe['ema12'], dataframe['ema26']) &
        #     # qtpylib.crossed_above(dataframe['ema_s'], dataframe['tema_s'])
        #     # qtpylib.crossed_below(dataframe['tema_s'], dataframe['dema_s'])
        #     (dataframe['rsi_6'] < dataframe['rsi_buy_hline'])
        #     # (dataframe['willr'] < dataframe['willr_buy_hline'])
        #     # & (dataframe['ema_width'] < -0.01)
        #     # (dataframe['ema200'] > dataframe['ema12']))
        #     |
        #     (True)
        # )
        # # conditions.append(
        # #     (dataframe['rsi_15'] < dataframe['rsi_buy_hline'])
        # #     # & (dataframe['ema_width'] < -0.01)
        # #     # & (dataframe['ema200'] > dataframe['ema12'])
        # # )

        # if conditions:
        #     dataframe.loc[reduce(lambda x, y: x & y, conditions), 'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        if self.sell_signal_1:
            conditions = [
                dataframe["adx"] < dataframe["adx_trendline"],
                dataframe["close"] > dataframe["ema_m"],
                dataframe["close"] > dataframe["close"].shift(1),
                qtpylib.crossed_below(dataframe['tema_s'], dataframe['dema_s']),
                # dataframe["low"] < dataframe["s1_ema_xxl"],
                # dataframe["close"] > dataframe["s1_ema_xxl"],
                # qtpylib.crossed_above(dataframe["s1_ema_sm"], dataframe["s1_ema_md"]),
                # dataframe["s1_ema_xs"] < dataframe["s1_ema_xl"],
                dataframe["volume"] > 0,
            ]
            dataframe.loc[reduce(lambda x, y: x & y, conditions), ["sell", "sell_tag"]] = (1, "sell_signal_1")

        # if self.sell_signal_2:
        #     conditions = [
        #         # qtpylib.crossed_above(dataframe["s2_fib_lower_band"], dataframe["s2_bb_lower_band"]),
        #         # dataframe["close"] < dataframe["s2_ema"],
        #         qtpylib.crossed_below(dataframe['ema_s'], dataframe['dema_s']),
        #         dataframe["rmi_up_trend"] == 1,
        #         # dataframe["rmi_up"] == 0,
        #         dataframe["volume"] > 0,
        #     ]
        #     dataframe.loc[reduce(lambda x, y: x & y, conditions), ["sell", "sell_tag"]] = (1, "sell_signal_2")

        # conditions = []
        #
        # conditions.append(
        #     # qtpylib.crossed_below(dataframe['ema12'], dataframe['ema26']) &
        #     # qtpylib.crossed_above(dataframe['tema_s'], dataframe['dema_s'])
        #     (dataframe['rsi_6'] > dataframe['rsi_sell_hline'])
        #     # (dataframe['willr'] > dataframe['willr_sell_hline'])
        #     # & (dataframe['ema_width'] > 0.01)
        #     # & (dataframe['ema200'] < dataframe['ema12'])
        # )
        # conditions.append(
        # (dataframe['rsi_6'] > dataframe['rsi_sell_hline'])
        #     # & (dataframe['ema_width'] < -0.01)
        #     # & (dataframe['ema200'] > dataframe['ema12'])
        # )

        # if conditions:
        #     dataframe.loc[reduce(lambda x, y: x & y, conditions), 'sell'] = 1

        return dataframe


def RMI(dataframe, *, length=20, mom=5):
    """
    Source: https://github.com/freqtrade/technical/blob/master/technical/indicators/indicators.py#L912
    """
    df = dataframe.copy()

    df['maxup'] = (df['close'] - df['close'].shift(mom)).clip(lower=0)
    df['maxdown'] = (df['close'].shift(mom) - df['close']).clip(lower=0)

    df.fillna(0, inplace=True)

    df["emaInc"] = ta.EMA(df, price='maxup', timeperiod=length)
    df["emaDec"] = ta.EMA(df, price='maxdown', timeperiod=length)

    df['RMI'] = np.where(df['emaDec'] == 0, 0, 100 - 100 / (1 + df["emaInc"] / df["emaDec"]))

    return df["RMI"]


## smoothed Heiken Ashi
def HA(self, dataframe, smoothing=None):
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
            df['Smooth_HA_O'] = ta.EMA(df['HA_Open'], sml)
            df['Smooth_HA_C'] = ta.EMA(df['HA_Close'], sml)
            df['Smooth_HA_H'] = ta.EMA(df['HA_High'], sml)
            df['Smooth_HA_L'] = ta.EMA(df['HA_Low'], sml)

    return df
