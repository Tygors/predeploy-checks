def apply_discount(price, percent):
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)


def _check_balance(balance, amount):
    return amount <= balance


def transfer(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if not _check_balance(balance, amount):
        raise ValueError("insufficient funds")
    return balance - amount
