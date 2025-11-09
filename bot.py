# bot.py
import json, logging
from binance import Client
from strategies.candlestick import get_candle_signal
from strategies.rsi import get_rsi_signal
from strategies.trend import get_trend_signal
from ml_model import MLModel
from risk_manager import RiskManager
from state_manager import StateManager

logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

state = StateManager.load("state.json")
balance = state.data.get("balance", 10000)
positions = state.data.get("positions", [])

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
client = Client(api_key, api_secret, testnet=True)

ml = MLModel()
risk = RiskManager(balance)
order_executed = False

try:
    klines = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR, limit=100)
    closes = [float(k[4]) for k in klines]
    
    cs_signal = get_candle_signal(klines)
    rsi_signal = get_rsi_signal(closes)
    trend_signal = get_trend_signal(closes)
    logging.info(f"Signals: candlestick={cs_signal}, RSI={rsi_signal}, trend={trend_signal}")

    ml_signal = ml.predict(closes, [cs_signal, rsi_signal, trend_signal])
    logging.info(f"ML model predicts: {ml_signal}")

    if ml_signal == 1 and (cs_signal == 1 or rsi_signal == 1 or trend_signal == 1):
        price = closes[-1]
        stop_price = risk.calculate_stop(price, direction=1)
        qty = risk.calculate_size(price, stop_price)
        order = client.order_market_buy(symbol='BTCUSDT', quantity=qty)
        logging.info(f"Executed BUY {qty} @ {price}")
        positions.append({'side': 'LONG', 'entry': price, 'qty': qty, 'stop': stop_price})
        order_executed = True

    elif ml_signal == -1 and (cs_signal == -1 or rsi_signal == -1 or trend_signal == -1):
        price = closes[-1]
        stop_price = risk.calculate_stop(price, direction=-1)
        qty = risk.calculate_size(price, stop_price)
        order = client.order_market_sell(symbol='BTCUSDT', quantity=qty)
        logging.info(f"Executed SELL {qty} @ {price}")
        positions.append({'side': 'SHORT', 'entry': price, 'qty': qty, 'stop': stop_price})
        order_executed = True
    else:
        logging.info("No trade signal this run.")

    if order_executed:
        balance = float(client.get_asset_balance(asset='USDT')['free'])
        state.update(balance, positions)
    StateManager.save("state.json", state.data)
    logging.info("State saved.")

except Exception as e:
    logging.error(f"Error in bot run: {e}", exc_info=True)
    StateManager.save("state.json", state.data)
    raise
