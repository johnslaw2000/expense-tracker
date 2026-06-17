from flask import Flask,  render_template, request, redirect,url_for
import psycopg2
import os
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

def get_db():
    conn = psycopg2.connect(
        dbname = os.environ.get("DB_NAME", "expensedb"),
        user = os.environ.get("DB_USER", "expenseuser"),
        password = os.environ.get("DB_PASS", "expensepass"),
        host = os.environ.get("DB_HOST", "db") 

    )
    return conn




def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
        id SERIAL PRIMARY KEY,
        description VARCHAR(100) NOT NULL,
        amount NUMERIC NOT NULL,
        category VARCHAR(50) NOT NULL,
        date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)
    conn.commit()
    cur.close()
    conn.close() 
    

@app.route('/')
def home():
    conn = get_db()
    cur =conn.cursor()
    cur.execute("SELECT * FROM expenses ORDER BY date_added DESC")
    expenses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']  
    
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
        "INSERT INTO expenses (description, amount, category) VALUES(%s, %s, %s)", (description, amount, category)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('home'))

    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('home'))

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
