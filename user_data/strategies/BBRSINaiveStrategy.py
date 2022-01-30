# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy.interface import IStrategy

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class BBRSINaiveStrategy(IStrategy):
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        # "30": 0.04,
        # "20": 0.06,
        "0": 100
        # "0": 0.08
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.8

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal ticker interval for the strategy.
    timeframe = '4h'

    # Run "populate_indicators()" only for new candle.
    # process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 200

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }

    plot_config = {
        'main_plot': {
            # 'bb_midband': {'color': 'blue'},
            'sma50': {'color': 'red'},
            'sma100': {},
            'ema21': {'color': 'green'},
            'ema50': {'color': 'orange'},
            'ema100': {'color': 'pink'},
            'ema150': {'color': 'brown'},
            'ema200': {'color': 'purple'},
            'BBANDS_U': {},
            'BBANDS_M': {},
            'BBANDS_L': {},
        },
        'subplots': {
            "RSI": {
                'rsi': {'color': 'yellow'},
            }
        }
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=15)

        # Bollinger bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['bb_midband'] = bollinger['mid']
        dataframe['bb_lowerband'] = bollinger['lower']

        bb = ta.BBANDS(dataframe, window=20, stds=2)
        # print(bb)

        dataframe['BBANDS_U'] = bb["upperband"]
        dataframe['BBANDS_M'] = bb["middleband"]
        dataframe['BBANDS_L'] = bb["lowerband"]

        weighted_bollinger = qtpylib.weighted_bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=2
        )
        dataframe["wbb_upperband"] = weighted_bollinger["upper"]
        dataframe["wbb_lowerband"] = weighted_bollinger["lower"]
        dataframe["wbb_middleband"] = weighted_bollinger["mid"]
        dataframe["wbb_percent"] = (
                (dataframe["close"] - dataframe["wbb_lowerband"]) /
                (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"])
        )
        dataframe["wbb_width"] = (
                (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"]) /
                dataframe["wbb_middleband"]
        )

        # # EMA - Exponential Moving Average
        dataframe['ema3'] = ta.EMA(dataframe, timeperiod=3)
        # dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        # dataframe['ema10'] = ta.EMA(dataframe, timeperiod=10)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)
        dataframe['ema150'] = ta.EMA(dataframe, timeperiod=150)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)

        dataframe['sma50'] = ta.SMA(dataframe, timeperiod=30)
        dataframe['sma100'] = ta.SMA(dataframe, timeperiod=100)

        dataframe["rsi_buy_hline"] = 25
        dataframe["rsi_sell_hline"] = 60

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['rsi'] > 25)  # Signal: RSI is greater 25
                    & qtpylib.crossed_below(dataframe['sma50'], dataframe['ema21'])
                    & (dataframe['close'] > dataframe['ema100'])
                # & (dataframe['high'] > dataframe['bb_lowerband'])  # Signal: price is less than lower bb
                # & (dataframe['high'] > dataframe['bb_lowerband'])  # Signal: price is less than lower bb
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # (dataframe['rsi'] > 70)  # Signal: RSI is greater 70
                qtpylib.crossed_above(dataframe['sma50'], dataframe['ema21'])
                # & (dataframe['close'] > dataframe['bb_midband'])  # Signal: price is greater than mid bb
            ),
            'sell'] = 1

        return dataframe
