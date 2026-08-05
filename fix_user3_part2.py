import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    # Check if they have a TCS investment
    cur.execute('SELECT investment_id, quantity, purchase_price FROM investments WHERE user_id = 3 AND asset_name = %s', ('TCS',))
    tcs = cur.fetchone()
    if tcs:
        # they said 'delete that 1000000000000 fund in investment' - maybe they meant the TCS investment? No, TCS is 24,130. 1 billion is the deposit.
        pass
        
    # Reset savings pool from negative to 0
    cur.execute('UPDATE users SET savings_pool = 0 WHERE user_id = 3 AND savings_pool < 0')
    
    conn.commit()
    cur.close()
    conn.close()
    print('Reset negative savings pool.')
except Exception as e:
    print('Error:', e)
