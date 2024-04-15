import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime

# Instantiate Flask app
app = Flask(__name__)

# Function to initialize the database
def init_db():
    # Connect to the database
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    
    # Create todo_list table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todo_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            date_created TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Route to add a new todo list item
@app.route("/todolist", methods=["POST"])
def add_todo():
    try:
        # Extract data from JSON request
        data = request.json
        name = data.get('name')
        description = data.get('description')
        completed = data.get('completed', 0)  # Default value of completed is 0
        date_created = datetime.utcnow().isoformat()  # Current timestamp

        # Validate input
        if not name or not description:
            return jsonify({"error": "Name and description are required."}), 400

        # Add the new todo to the database
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO todo_list (name, description, completed, date_created) VALUES (?, ?, ?, ?)',
                       (name, description, completed, date_created))
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({"message": "Todo added successfully."}), 201
    
    except Exception as e:
        # Return error response for invalid request
        return jsonify({"error": "Invalid request."}), 400

# Route to get all todo list items
@app.route("/todolist", methods=["GET"])
def get_todolist():
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todo_list')
    todo_list = cursor.fetchall()
    conn.close()
    return jsonify(todo_list)

# Route to get a single todo item by its ID
@app.route("/todolist/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    conn = sqlite3.connect('database.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todo_list WHERE id = ?', (todo_id,))
    todo_item = cursor.fetchone()
    conn.close()
    if todo_item:
        return jsonify(todo_item)
    else:
        return jsonify({"error": "Todo item not found."}), 404

# Route to update a todo item by its ID
@app.route("/todolist/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    try:
        # Extract data from JSON request
        data = request.json
        name = data.get('name')
        description = data.get('description')
        completed = data.get('completed')

        # Update the todo item in the database
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE todo_list 
            SET name = ?, description = ?, completed = ?
            WHERE id = ?
            ''', (name, description, completed, todo_id))
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({"message": "Todo item updated successfully."})
    
    except Exception as e:
        # Return error response for invalid request
        return jsonify({"error": "Invalid request."}), 400

# Route to delete a todo item by its ID
@app.route("/todolist/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    try:
        # Delete the todo item from the database
        conn = sqlite3.connect('database.sqlite3')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM todo_list WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close()

        # Return success response
        return jsonify({"message": "Todo item deleted successfully."})
    
    except Exception as e:
        # Return error response for invalid request
        return jsonify({"error": "Invalid request."}), 400

if __name__ == "__main__":
    # Run the Flask app in debug mode
    app.run(debug=True)
