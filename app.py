from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_db_connection():
    conn = sqlite3.connect('enhanced_menu_management.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('adminpanel.html')

@app.route('/api/menu_items', methods=['GET', 'POST'])
def menu_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        # Fetch menu items
        try:
            cursor.execute('''
                SELECT 
                    mi.MenuItemID, 
                    mi.Name, 
                    mi.Description, 
                    mi.Price, 
                    mi.ImageURL, 
                    mi.AvailabilityStatus,
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
            return jsonify([dict(item) for item in menu_items])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()

    elif request.method == 'POST':
        # Add new menu item
        data = request.json
        try:
            cursor.execute('''
                INSERT INTO MenuItems 
                (Name, Description, Price, CategoryID, AvailabilityStatus, ImageURL) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['Name'], 
                data['Description'], 
                float(data['Price']), 
                int(data['CategoryID']), 
                data.get('AvailabilityStatus', 1),
                data.get('ImageURL', '')
            ))
            menu_item_id = cursor.lastrowid

            if 'DietaryPreferences' in data and data['DietaryPreferences']:
                cursor.executemany('''
                    INSERT INTO MenuItemDietaryPreferences (MenuItemID, PreferenceID) 
                    VALUES (?, ?)
                ''', [(menu_item_id, pref_id) for pref_id in data['DietaryPreferences']])

            conn.commit()
            return jsonify({"message": "Menu item added successfully", "id": menu_item_id}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            conn.close()

@app.route('/api/menu_items/<int:item_id>', methods=['PUT', 'DELETE'])
def modify_menu_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'PUT':
        # Update existing menu item
        data = request.json
        try:
            cursor.execute('''
                UPDATE MenuItems 
                SET Name=?, Description=?, Price=?, CategoryID=?, 
                    AvailabilityStatus=?, ImageURL=? 
                WHERE MenuItemID=?
            ''', (
                data['Name'], 
                data['Description'], 
                float(data['Price']), 
                int(data['CategoryID']), 
                data.get('AvailabilityStatus', 1),
                data.get('ImageURL', ''),
                item_id
            ))

            cursor.execute('DELETE FROM MenuItemDietaryPreferences WHERE MenuItemID=?', (item_id,))

            if 'DietaryPreferences' in data and data['DietaryPreferences']:
                cursor.executemany('''
                    INSERT INTO MenuItemDietaryPreferences (MenuItemID, PreferenceID) 
                    VALUES (?, ?)
                ''', [(item_id, pref_id) for pref_id in data['DietaryPreferences']])

            conn.commit()
            return jsonify({"message": "Menu item updated successfully"}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            conn.close()

    elif request.method == 'DELETE':
        # Delete menu item
        try:
            cursor.execute('DELETE FROM MenuItemDietaryPreferences WHERE MenuItemID=?', (item_id,))
            cursor.execute('DELETE FROM MenuItems WHERE MenuItemID=?', (item_id,))
            conn.commit()
            return jsonify({"message": "Menu item deleted successfully"}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            conn.close()

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM Category')
        categories = cursor.fetchall()
        return jsonify([dict(category) for category in categories])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/dietary_preferences', methods=['GET'])
def get_dietary_preferences():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM DietaryPreferences')
        preferences = cursor.fetchall()
        return jsonify([dict(preference) for preference in preferences])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
