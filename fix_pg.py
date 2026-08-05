import psycopg2

try:
    conn = psycopg2.connect('postgresql://neondb_owner:npg_EfHdSh41vKQl@ep-twilight-wave-ayv8l0z7-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT investment_id, asset_name, quantity, purchase_price, is_active FROM investments')
    all_invs = cur.fetchall()
    
    for inv in all_invs:
        print(f'{inv[0]}: {inv[1]} - Qty: {inv[2]} - Price: {inv[3]} - Active: {inv[4]}')
        
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
