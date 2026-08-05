import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT transaction_id, description, amount, category_id, transaction_date FROM transactions')
    all_txs = cur.fetchall()
    
    for t in all_txs:
        if t[2] > 100000:
            print(f'{t[0]}: {t[1]} - Amount: {t[2]} - Date: {t[4]}')
            
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
