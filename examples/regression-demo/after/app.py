def apply_discount(price, percent):
    if percent < 0 or percent >= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


def transfer(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount


def receipt(order):
    return {"amount": order["total"], "currency": "USD"}


def fee(amount):
    return round(amount * 0.03, 2)
