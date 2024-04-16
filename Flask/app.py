import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime

# გლობალური ცვლადები ბაზასთან დასაკავშირებლად
DB_NAME = 'db.sqlite3'

# Flask app შექმნა
app = Flask(__name__)

# ბაზის შექმნა
def init_db():
    # ბაზასთან დაკავშირება
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # შექმნის inventari ცხრილს თუ არ არის შექმნილი
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            barcode TEXT,
            amount INTEGER DEFAULT 1,
            buy_date TEXT DEFAULT CURRENT_DATE
        )
    ''')
    
    # შეინახავს ცვლილებებს და დახურავს ბაზას
    conn.commit()
    conn.close()

# ფუნქციის გამოძახება: ბაზის შექმნა
init_db()

# ახალი ნივთის დამატება
@app.route("/api", methods=["POST"])
def add_item():
    try:
        # Extract data from JSON request
        data = request.json
        name = data.get('name')
        barcode = data.get('barcode')
        amount = data.get('amount', 1)  # ნივთის რაოდენობა ჩაიწერება 1 თუ ცალრიელს დავტოვებთ
        buy_date = data.get('buy_date', datetime.utcnow().date().isoformat())  # ყიდვის თარიღად ჩაიწერება ნივთის დამატების დრო

        # შემოწმება ნივთის სახელი რომ არ დარჩეს ცარიელი
        if not name:
            return jsonify({"error": "Inventari Name is empty, please enter item Name."}), 400

        # დაემატება ახალი ნივთი ბაზაში
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO inventari (name, barcode, amount, buy_date) VALUES (?, ?, ?, ?)',
                       (name, barcode, amount, buy_date))
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({"message": "Inventari added successfully."}), 201
    
    except Exception:
        # Return error response for invalid request
        return jsonify({"error": "Invalid request."}), 400

# დააბრუნებს ყველა ნივთის აღწერას ბაზიდან
@app.route("/api", methods=["GET"])
def get_items():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inventari')
    item_list = cursor.fetchall()
    conn.close()
    return jsonify(item_list)

# ბაზიდან აბრუნებს ერთ ნივთს კონკრეტული id-ის მიხედვით
@app.route("/api/<int:inv_id>", methods=["GET"])
def get_item(inv_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inventari WHERE id = ?', (inv_id,))
    one_item = cursor.fetchone()
    conn.close()

    if one_item:
        return jsonify(one_item)
    else:
        return jsonify({"error": "Inventari item not found."}), 404

# ბაზაში არსებული ნივთის აღწერის განახლება კონკრეტული id-ით
@app.route("/api/<int:inv_id>", methods=["PUT"])
def update_item(inv_id):
    try:
        # Extract data from JSON request
        data = request.json
        name = data.get('name')
        barcode = data.get('barcode')
        amount = data.get('amount')
        buy_date = data.get('buy_date')

        # ბაზაში ნივთის აღწერის განახლება
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE inventari 
            SET name = ?, barcode = ?, amount = ?, buy_date = ?
            WHERE id = ?
            ''', (name, barcode, amount, buy_date, inv_id))
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({"message": "Inventari item updated successfully."})
    
    except Exception:
        # Return error response for invalid request
        return jsonify({"error": "Invalid request."}), 400

# ბაზიდან ნივთის წაშლა კონკრეტული id-ის მიხედვით
@app.route("/api/<int:inv_id>", methods=["DELETE"])
def delete_item(inv_id):
    try:
        # ბაზიდაბ კონკრეტული ნივთის წაშლა
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inventari WHERE id = ?', (inv_id,))
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({"message": "Inventari item deleted successfully."})
    
    except Exception:
        # Return error response for invalid request
        return jsonify({"error": "Invalid request."}), 400

if __name__ == "__main__":
    # Flask app სერვერის გაშვება ლოკალურად
    app.run(debug=True, host='127.0.0.1', port=5000)
