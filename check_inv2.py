import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT investment_id, asset_name, quantity, purchase_price, is_active FROM investments')
    all_invs = cur.fetchall()
    
    for t in all_invs:
        qty = t[2] if t[2] else 0
        price = t[3] if t[3] else 0
        cost = qty * price
        if cost > 1000000:
            print(f'{t[0]}: {t[1]} - Qty: {qty} - Price: {price} - Cost: {cost} - Active: {t[4]}')
            
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
