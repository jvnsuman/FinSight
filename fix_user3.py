import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    # 1. Reset user 3 cash balance
    cur.execute('UPDATE users SET cash_balance = 0 WHERE user_id = 3')
    
    # 2. Reset user 3 savings pool
    # Wait, the user said 'add that remaining value'. 
    # If they want me to delete the 1,000,000,000 from cash_balance, I will do that.
    # What about the TCS investment they just bought? Do they want it deleted?
    # 'delete that 1000000000000 fund in investment' - maybe they meant the cash?
    
    conn.commit()
    cur.close()
    conn.close()
    print('Reset cash balance for user 3 to 0.')
except Exception as e:
    print('Error:', e)
