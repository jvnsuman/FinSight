import psycopg2
from decimal import Decimal
import datetime
import calendar

conn = psycopg2.connect('postgresql://neondb_owner:npg_EfHdSh41vKQl@ep-twilight-wave-ayv8l0z7-pooler.c-5.us-east-2.aws.neon.tech/neondb?sslmode=require')
cur = conn.cursor()

# Get July bounds
today = datetime.date.today()
current_month = today.replace(day=1)
previous_month = current_month - datetime.timedelta(days=1)
first_day = previous_month.replace(day=1)
last_day = previous_month.replace(day=calendar.monthrange(previous_month.year, previous_month.month)[1])

# For now, let's just reset all users savings pool to their total lifetime net (excluding august)
cur.execute("SELECT user_id, email, savings_pool FROM users")
users = cur.fetchall()

for u in users:
    uid = u[0]
    email = u[1]
    
    cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND transaction_type = 'income' AND transaction_date < '2026-08-01'", (uid,))
    income = cur.fetchone()[0] or 0
    
    cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND transaction_type = 'expense' AND transaction_date < '2026-08-01'", (uid,))
    expense = cur.fetchone()[0] or 0
    
    net = Decimal(str(income)) - Decimal(str(expense))
    if net < 0:
        net = Decimal("0")
        
    cur.execute("UPDATE users SET savings_pool = %s WHERE user_id = %s", (net, uid))
    print(f"Updated user {uid} ({email}) savings_pool to {net}")

conn.commit()
cur.close()
conn.close()
