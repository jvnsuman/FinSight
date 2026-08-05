import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT transaction_id, description, amount, category_id, date FROM transactions WHERE amount > 1000000')
    massive = cur.fetchall()
    
    print('Transactions:')
    for t in massive:
        print(f'{t[0]}: {t[1]} - Amount: {t[2]} - Date: {t[4]}')
        
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
