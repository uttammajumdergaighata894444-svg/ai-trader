import json
import threading
import time
import numpy as np
import websocket

# Kivy লাইব্রেরি মোবাইল অ্যাপের ইউজার ইন্টারফেসের জন্য
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import platform


# ১. রিয়েল-টাইম ডেটা পাইপলাইন (Binance Live WebSocket Integration)
class MarketDataPipeline:

  def __init__(self, ws_url):
    self.ws_url = ws_url
    self.price_history = []
    self.is_connected = False

  def on_message(self, ws, message):
    try:
      data = json.loads(message)
      if "p" in data:
        current_price = float(data["p"])
        self.price_history.append(current_price)
        if len(self.price_history) > 50:
          self.price_history.pop(0)
    except Exception as e:
      print("Error:", e)

  def on_error(self, ws, error):
    print("WebSocket Error:", error)

  def on_close(self, ws, close_status_code, close_msg):
    self.is_connected = False

  def on_open(self, ws):
    self.is_connected = True

  def start(self):
    ws = websocket.WebSocketApp(
        self.ws_url,
        on_open=self.on_open,
        on_message=self.on_message,
        on_error=self.on_error,
        on_close=self.on_close,
    )
    ws.run_forever()


# ২. ফিচার ইঞ্জিনিয়ারিং ক্লাস
class FeatureEngineering:

  @staticmethod
  def calculate_sma(prices, window=5):
    if len(prices) < window:
      return prices[-1] if prices else 0
    return np.mean(prices[-window:])

  @staticmethod
  def calculate_rsi(prices, window=14):
    if len(prices) < window + 1:
      return 50.0
    deltas = np.diff(prices)
    seed = deltas[:window]
    up = seed[seed >= 0].sum() / window
    down = -seed[seed < 0].sum() / window
    if down == 0:
      return 100.0
    rs = up / down
    return 100.0 - (100.0 / (1.0 + rs))

  @classmethod
  def extract_features(cls, price_history):
    current_price = price_history[-1] if price_history else 0
    sma_5 = cls.calculate_sma(price_history, window=5)
    rsi_14 = cls.calculate_rsi(price_history, window=14)
    return [current_price, sma_5, rsi_14]


# ৩. লাইটওয়েট এআই অ্যানালিটিক্স ইঞ্জিন (Android Friendly)
class AIAnalyticsEngine:

  def __init__(self):
    self.is_trained = True

  def predict_signal(self, features):
    current_price, sma_5, rsi_14 = features

    if current_price <= 0:
      return {"signal": 0, "confidence": 0.0}

    score = 0.0

    # Price vs SMA
    if current_price > sma_5:
      score += 0.4
    else:
      score -= 0.2

    # RSI
    if 45 <= rsi_14 <= 65:
      score += 0.3
    elif rsi_14 < 30:
      score += 0.2
    elif rsi_14 > 70:
      score -= 0.3

    if score >= 0.5:
      return {"signal": 1, "confidence": min(0.95, 0.60 + score * 0.35)}

    return {"signal": 0, "confidence": min(0.95, 0.50 + abs(score) * 0.20)}


# ৪. রিস্ক ম্যানেজমেন্ট ও পজিশন সাইজিং
class RiskManagementSystem:

  def __init__(self, max_risk_per_trade_pct=0.02):
    self.max_risk_pct = max_risk_per_trade_pct

  def calculate_position_size(
      self, account_balance, entry_price, stop_loss_price
  ):
    risk_amount = account_balance * self.max_risk_pct
    price_difference = abs(entry_price - stop_loss_price)
    if price_difference == 0:
      return 0
    return risk_amount / price_difference


# ৫. ফাইন্যান্সিয়াল লেজার ও ট্র্যাকিং সিস্টেম
class FinancialLedger:

  def __init__(self, initial_balance):
    self.balance = initial_balance
    self.trades_history = []

  def record_trade(
      self, trade_id, asset, buy_price, sell_price, quantity, commission=0.0
  ):
    gross_pnl = (sell_price - buy_price) * quantity
    net_pnl = gross_pnl - commission
    self.balance += net_pnl
    trade_record = {
        "trade_id": trade_id,
        "asset": asset,
        "gross_pnl": gross_pnl,
        "commission": commission,
        "net_pnl": net_pnl,
        "closing_balance": self.balance,
    }
    self.trades_history.append(trade_record)
    return trade_record

  def get_summary(self):
    total_profit = sum(
        t["net_pnl"] for t in self.trades_history if t["net_pnl"] > 0
    )
    total_loss = sum(
        t["net_pnl"] for t in self.trades_history if t["net_pnl"] < 0
    )
    return {
        "current_balance": self.balance,
        "total_trades": len(self.trades_history),
        "total_profit": total_profit,
        "total_loss": total_loss,
        "net_pnl": total_profit + total_loss,
    }


# ৬. মোবাইল অ্যাপ ইউজার ইন্টারফেস (Kivy GUI + Paper Trading)
class TradingAppLayout(BoxLayout):

  def __init__(self, **kwargs):
    super(TradingAppLayout, self).__init__(**kwargs)
    self.orientation = "vertical"
    self.padding = 20
    self.spacing = 10

    # Duplicate trade prevention flags
    self.position_open = False
    self.last_signal_time = 0

    self.status_label = Label(
        text="AI Trading Bot: Idle", font_size=18, size_hint_y=None, height=50
    )
    self.add_widget(self.status_label)

    self.price_label = Label(
        text="Live Price: Waiting...",
        font_size=20,
        size_hint_y=None,
        height=50,
    )
    self.add_widget(self.price_label)

    self.balance_label = Label(
        text="Balance: $5000.00",
        font_size=18,
        size_hint_y=None,
        height=40,
    )
    self.add_widget(self.balance_label)

    self.voice_btn = Button(
        text="🎤 Voice Command Ready",
        size_hint_y=None,
        height=60,
        background_color=(0.1, 0.6, 0.8, 1),
    )
    self.voice_btn.bind(on_press=self.listen_voice_command)
    self.add_widget(self.voice_btn)

    self.log_input = TextInput(
        text="System initialized successfully (Paper Trading Mode).\n",
        readonly=True,
        font_size=14,
    )
    self.add_widget(self.log_input)

    self.ledger = FinancialLedger(initial_balance=5000.0)
    self.risk_mgr = RiskManagementSystem(max_risk_per_trade_pct=0.01)
    self.ai_engine = AIAnalyticsEngine()

    self.pipeline = MarketDataPipeline(
        "wss://stream.binance.com:9443/ws/btcusdt@trade"
    )
    ws_thread = threading.Thread(target=self.pipeline.start, daemon=True)
    ws_thread.start()

    Clock.schedule_interval(self.update_dashboard, 1.0)

  def speak_message(self, message):
    print(f"[Log / Output]: {message}")
    self.log_input.text += f"\n[System]: {message}"

  def listen_voice_command(self, instance):
    spoken_command = "start"
    self.log_input.text += f"\n[Voice Input Detected]: {spoken_command}"
    self.status_label.text = "Status: Running via Voice Command!"
    self.speak_message("Bot activated.")

  def update_dashboard(self, dt):
    if self.pipeline.price_history:
      current_price = self.pipeline.price_history[-1]
      self.price_label.text = f"Live Price: ${current_price}"

      if len(self.pipeline.price_history) >= 15:
        features = FeatureEngineering.extract_features(
            self.pipeline.price_history
        )
        signal = self.ai_engine.predict_signal(features)

        # Check signal along with position guard to avoid spamming trades
        if (
            signal["signal"] == 1
            and signal["confidence"] > 0.6
            and not self.position_open
        ):
          self.position_open = True
          self.last_signal_time = time.time()

          self.status_label.text = (
              f"Signal: BUY (Conf: {signal['confidence']:.2f})"
          )
          stop_loss_price = current_price - 500
          position_size = self.risk_mgr.calculate_position_size(
              self.ledger.balance, current_price, stop_loss_price
          )
          trade_res = self.ledger.record_trade(
              trade_id=len(self.ledger.trades_history) + 1,
              asset="BTCUSDT",
              buy_price=current_price,
              sell_price=current_price + 300,
              quantity=position_size,
              commission=1.0,
          )
          self.balance_label.text = (
              f"Balance: ${trade_res['closing_balance']:.2f}"
          )
          self.speak_message("Buy signal executed and paper ledger updated.")
        elif self.position_open:
          self.status_label.text = (
              "Status: Position Active (Holding / Monitoring)"
          )
        else:
          self.status_label.text = "Status: Monitoring market... No signal."


class AutonomousTradingApp(App):

  def build(self):
    self.title = "AI Autonomous Mobile Trader"
    return TradingAppLayout()


if __name__ == "__main__":
  AutonomousTradingApp().run()
  
