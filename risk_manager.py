# risk_manager.py
class RiskManager:
    def __init__(self, balance):
        self.balance = balance
        self.risk_pct = 0.02

    def calculate_size(self, price, stop_price):
        risk_amount = self.balance * self.risk_pct
        risk_per_unit = abs(price - stop_price)
        if risk_per_unit <= 0:
            return 0
        qty = risk_amount / risk_per_unit
        return round(qty, 6)

    def calculate_stop(self, entry_price, direction):
        if direction == 1:
            return entry_price * 0.98
        else:
            return entry_price * 1.02
