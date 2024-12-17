from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('enhanced_menu_management.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/menu_items', methods=['GET'])
def get_menu_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            mi.MenuItemID, 
            mi.Name, 
            mi.Description, 
            mi.Price, 
            mi.ImageURL, 
            c.CategoryName,
            c.CategoryID,
            GROUP_CONCAT(dp.PreferenceName, ', ') as DietaryPreferences
        FROM MenuItems mi
        LEFT JOIN Category c ON mi.CategoryID = c.CategoryID
        LEFT JOIN MenuItemDietaryPreferences midp ON mi.MenuItemID = midp.MenuItemID
        LEFT JOIN DietaryPreferences dp ON midp.PreferenceID = dp.PreferenceID
        GROUP BY mi.MenuItemID
    ''')
    menu_items = cursor.fetchall()
    conn.close()
    return jsonify([dict(item) for item in menu_items])

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Category')
    categories = cursor.fetchall()
    conn.close()
    return jsonify([dict(category) for category in categories])
@app.route('/admin')
def admin():
    return render_template("adminpanel.html")
@app.route('/api/dietary_preferences', methods=['GET'])
def get_dietary_preferences():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM DietaryPreferences')
    preferences = cursor.fetchall()
    conn.close()
    return jsonify([dict(preference) for preference in preferences])

if __name__ == '__main__':
    app.run(debug=True)