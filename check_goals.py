import psycopg2

try:
    conn = psycopg2.connect('postgresql://REDACTED:REDACTED@REDACTED/REDACTED?sslmode=require')
    cur = conn.cursor()
    
    cur.execute('SELECT goal_id, name, target_amount, current_amount, status FROM goals')
    all_goals = cur.fetchall()
    
    print('Goals:')
    for g in all_goals:
        print(f'{g[0]}: {g[1]} - Target: {g[2]} - Current: {g[3]} - Status: {g[4]}')
        
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
