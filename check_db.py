from backend.database import SessionLocal
from backend.models.user import User
from backend.models.investment import Investment
from backend.models.trade import Trade

db = SessionLocal()
user = db.query(User).first()
if user:
    print('User:', user.email)
    print('Cash balance:', user.cash_balance)
    print('Savings pool:', user.savings_pool)
    
    investments = db.query(Investment).filter(Investment.user_id == user.user_id).all()
    print('\nInvestments:')
    for inv in investments:
        print(f'ID: {inv.investment_id}, Name: {inv.asset_name}, Quantity: {inv.quantity}, Purchase Price: {inv.purchase_price}, Active: {inv.is_active}')
        
    trades = db.query(Trade).filter(Trade.user_id == user.user_id).all()
    print('\nTrades:')
    for t in trades:
        print(f'ID: {t.trade_id}, Action: {t.action}, Qty: {t.quantity}, Price: {t.price}, Source: {t.source}')
