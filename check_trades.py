import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT trade_id, action, quantity, price FROM trades')
    all_trades = cur.fetchall()
    
    print('Trades:')
    for t in all_trades:
        if t[3] > 1000000 or (t[2] and t[2] > 1000000):
            print(f'{t[0]}: {t[1]} - Qty: {t[2]} - Price: {t[3]}')
        
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
