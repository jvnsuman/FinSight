import psycopg2

try:
    conn = psycopg2.connect('postgresql://neondb_owner:npg_EfHdSh41vKQl@ep-twilight-wave-ayv8l0z7-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT trade_id, action, quantity, price FROM trades')
    all_trades = cur.fetchall()
    
    for t in all_trades:
        price = t[3] if t[3] is not None else 0
        qty = t[2] if t[2] is not None else 0
        if price > 1000000 or qty > 1000000:
            print(f'Trade: {t[0]}: {t[1]} - Qty: {t[2]} - Price: {t[3]}')
            
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
