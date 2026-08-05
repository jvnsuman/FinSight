import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT investment_id, asset_name, quantity, purchase_price, is_active FROM investments')
    all_invs = cur.fetchall()
    
    for inv in all_invs:
        print(f'{inv[0]}: {inv[1]} - Qty: {inv[2]} - Price: {inv[3]} - Active: {inv[4]}')
        
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
