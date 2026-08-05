from backend.database import SessionLocal
import backend.models
from backend.models.user import User
from backend.models.investment import Investment
from backend.models.trade import Trade

db = SessionLocal()
user = db.query(User).first()
if user:
    print('User:', user.email)
    print('Cash balance:', user.cash_balance)
    print('Savings pool:', user.savings_pool)
    
    investments = db.query(Investment).filter(Investment.user_id == user.user_id, Investment.is_active == True).all()
    print('\nInvestments:')
    for inv in investments:
        if inv.quantity > 1000000 or inv.purchase_price > 1000000:
            print(f'Deleting massive investment: {inv.asset_name}')
            inv.is_active = False
            
            # Restore to savings pool
            user.savings_pool += (inv.quantity * inv.purchase_price)
            
    db.commit()
    print('Done.')
