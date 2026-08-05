import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT user_id, email, cash_balance, savings_pool FROM users')
    all_users = cur.fetchall()
    
    for u in all_users:
        print(f'{u[0]}: {u[1]} - Cash: {u[2]} - Savings: {u[3]}')
        
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
