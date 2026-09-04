import json
import threading
import time
import websocket

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


# ==========================================================
# 1. MARKET DATA PIPELINE
# ==========================================================

class MarketDataPipeline:
    def __init__(self, ws_url):  
        self.ws_url = ws_url  
        self.price_history = []  
        self.is_connected = False  
        self.lock = threading.Lock()  

    def on_message(self, ws, message):  
        try:  
            data = json.loads(message)  
            if "p" in data:  
                current_price = float(data["p"])  
                with self.lock:  
                    self.price_history.append(current_price)  
                    if len(self.price_history) > 100:  
                        self.price_history.pop(0)  
        except Exception as e:  
            print("WebSocket message error:", e)  

    def on_error(self, ws, error):  
        print("WebSocket error:", error)  

    def on_close(self, ws, close_status_code, close_msg):  
        self.is_connected = False  
        print("WebSocket closed:", close_status_code, close_msg)  

    def on_open(self, ws):  
        self.is_connected = True  
        print("WebSocket connected")  

    def start(self):  
        while True:  
            try:  
                ws = websocket.WebSocketApp(  
                    self.ws_url,  
                    on_open=self.on_open,  
                    on_message=self.on_message,  
                    on_error=self.on_error,  
                    on_close=self.on_close,  
                )  
                ws.run_forever(  
                    ping_interval=20,  
                    ping_timeout=10  
                )  
            except Exception as e:  
                print("WebSocket connection error:", e)  
            self.is_connected = False  
            time.sleep(5)


# ==========================================================
# 2. FEATURE ENGINEERING
# ==========================================================

class FeatureEngineering:
    @staticmethod  
    def calculate_sma(prices, window=5):  
        if not prices:  
            return 0.0  
        if len(prices) < window:  
            return prices[-1]  
        recent = prices[-window:]  
        return sum(recent) / len(recent)  

    @staticmethod  
    def calculate_rsi(prices, window=14):  
        if len(prices) < window + 1:  
            return 50.0  
        recent = prices[-(window + 1):]  
        gains = 0.0  
        losses = 0.0  
        for i in range(1, len(recent)):  
            delta = recent[i] - recent[i - 1]  
            if delta > 0:  
                gains += delta  
            elif delta < 0:  
                losses += abs(delta)  
        average_gain = gains / window  
        average_loss = losses / window  
        if average_loss == 0:  
            if average_gain > 0:  
                return 100.0  
            return 50.0  
        rs = average_gain / average_loss  
        return 100.0 - (100.0 / (1.0 + rs))  

    @classmethod  
    def extract_features(cls, price_history):  
        current_price = price_history[-1] if price_history else 0.0  
        sma_5 = cls.calculate_sma(price_history, window=5)  
        rsi_14 = cls.calculate_rsi(price_history, window=14)  
        return [current_price, sma_5, rsi_14]


# ==========================================================
# 3. AI ANALYTICS ENGINE
# ==========================================================

class AIAnalyticsEngine:
    def predict_signal(self, features):  
        current_price = features[0]  
        sma_5 = features[1]  
        rsi_14 = features[2]  

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

        # BUY  
        if score >= 0.5:  
            confidence = min(0.95, 0.60 + score * 0.35)  
            return {"signal": 1, "confidence": confidence}  

        # NO BUY  
        confidence = min(0.95, 0.50 + abs(score) * 0.20)  
        return {"signal": 0, "confidence": confidence}


# ==========================================================
# 4. RISK MANAGEMENT
# ==========================================================

class RiskManagementSystem:
    def __init__(self, max_risk_per_trade_pct=0.01):  
        self.max_risk_pct = max_risk_per_trade_pct  

    def calculate_position_size(self, account_balance, entry_price, stop_loss_price):  
        risk_amount = account_balance * self.max_risk_pct  
        price_difference = abs(entry_price - stop_loss_price)  
        if price_difference <= 0:  
            return 0.0  
        return risk_amount / price_difference


# ==========================================================
# 5. PAPER FINANCIAL LEDGER
# ==========================================================

class FinancialLedger:
    def __init__(self, initial_balance):  
        self.balance = float(initial_balance)  
        self.trades_history = []  

    def record_trade(self, trade_id, asset, buy_price, sell_price, quantity, commission=0.0):  
        gross_pnl = (sell_price - buy_price) * quantity  
        net_pnl = gross_pnl - commission  
        self.balance += net_pnl  

        trade_record = {  
            "trade_id": trade_id,  
            "asset": asset,  
            "buy_price": buy_price,  
            "sell_price": sell_price,  
            "quantity": quantity,  
            "net_pnl": net_pnl,  
            "closing_balance": self.balance  
        }  
        self.trades_history.append(trade_record)  
        return trade_record


# ==========================================================
# 6. KIVY UI
# ==========================================================

class TradingAppLayout(BoxLayout):
    def __init__(self, **kwargs):  
        super().__init__(**kwargs)  
        self.orientation = "vertical"  
        self.padding = 20  
        self.spacing = 10  
        self.position_open = False  

        # Status  
        self.status_label = Label(  
            text="AI Trading Bot: Idle",  
            font_size=18,  
            size_hint_y=None,  
            height=50  
        )  
        self.add_widget(self.status_label)  

        # Price  
        self.price_label = Label(  
            text="Live Price: Waiting...",  
            font_size=20,  
            size_hint_y=None,  
            height=50  
        )  
        self.add_widget(self.price_label)  

        # Balance  
        self.balance_label = Label(  
            text="Balance: $5000.00",  
            font_size=18,  
            size_hint_y=None,  
            height=40  
        )  
        self.add_widget(self.balance_label)  

        # Voice button  
        self.voice_btn = Button(  
            text="Voice Command Ready",  
            size_hint_y=None,  
            height=60  
        )  
        self.voice_btn.bind(on_press=self.listen_voice_command)  
        self.add_widget(self.voice_btn)  

        # Log  
        self.log_input = TextInput(  
            text="System initialized.\nPaper Trading Mode.\n",  
            readonly=True,  
            font_size=14  
        )  
        self.add_widget(self.log_input)  

        # Core systems  
        self.ledger = FinancialLedger(initial_balance=5000.0)  
        self.risk_mgr = RiskManagementSystem(max_risk_per_trade_pct=0.01)  
        self.ai_engine = AIAnalyticsEngine()  

        # Binance WebSocket  
        self.pipeline = MarketDataPipeline("wss://stream.binance.com:9443/ws/btcusdt@trade")  

        ws_thread = threading.Thread(  
            target=self.pipeline.start,  
            daemon=True  
        )  
        ws_thread.start()  

        # Dashboard update  
        Clock.schedule_interval(self.update_dashboard, 1.0)  

    def speak_message(self, message):  
        self.log_input.text += "\n[System]: " + message  

    def listen_voice_command(self, instance):  
        self.log_input.text += "\n[Voice Input Detected]: start"  
        self.status_label.text = "Status: Running via Command"  
        self.speak_message("Bot activated.")  

    def update_dashboard(self, dt):  
        prices = self.pipeline.price_history  

        if not prices:  
            self.status_label.text = "Status: Waiting for market data..."  
            return  

        current_price = prices[-1]  
        self.price_label.text = f"Live Price: ${current_price:.2f}"  

        if len(prices) < 15:  
            self.status_label.text = f"Collecting data... {len(prices)}/15"  
            return  

        features = FeatureEngineering.extract_features(prices)  
        signal = self.ai_engine.predict_signal(features)  

        if signal["signal"] == 1 and signal["confidence"] > 0.6 and not self.position_open:  
            self.position_open = True  
            self.status_label.text = f"Signal: BUY (Conf: {signal['confidence']:.2f})"  

            stop_loss_price = current_price - 500  
            position_size = self.risk_mgr.calculate_position_size(  
                self.ledger.balance,  
                current_price,  
                stop_loss_price  
            )  

            if position_size > 0:  
                trade_res = self.ledger.record_trade(  
                    trade_id=len(self.ledger.trades_history) + 1,  
                    asset="BTCUSDT",  
                    buy_price=current_price,  
                    sell_price=current_price + 300,  
                    quantity=position_size,  
                    commission=1.0  
                )  
                self.balance_label.text = f"Balance: ${trade_res['closing_balance']:.2f}"  
                self.speak_message("Paper BUY signal executed.")  

        elif self.position_open:  
            self.status_label.text = "Status: Position Active (Paper Monitoring)"  
        else:  
            self.status_label.text = "Status: Monitoring market..."


# ==========================================================
# APP & MAIN
# ==========================================================

class AutonomousTradingApp(App):
    def build(self):  
        self.title = "AI Autonomous Mobile Trader"  
        return TradingAppLayout()


if __name__ == "__main__":
    AutonomousTradingApp().run()
  
