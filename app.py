from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
from fpdf import FPDF

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
                    c.CategoryID
                FROM MenuItems mi
                LEFT JOIN Category c ON mi.CategoryID = c.CategoryID
            ''')
            menu_items = cursor.fetchall()
            return jsonify([dict(item) for item in menu_items])
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()

    elif request.method == 'POST':
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

            conn.commit()
            return jsonify({"message": "Menu item added successfully"}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            conn.close()

@app.route('/api/menu_items', methods=['PUT'])
def update_menu_item():
    try:
        data = request.json
        menu_item_id = data.get('MenuItemID')

        if not menu_item_id:
            return jsonify({"error": "MenuItemID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE MenuItems
            SET Name = ?, Description = ?, Price = ?, CategoryID = ?, ImageURL = ?, AvailabilityStatus = ?, ModifiedDate = CURRENT_TIMESTAMP
            WHERE MenuItemID = ?
        ''', (
            data.get('Name'),
            data.get('Description'),
            data.get('Price'),
            data.get('CategoryID'),
            data.get('ImageURL'),
            data.get('AvailabilityStatus'),
            menu_item_id
        ))

        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "No menu item found with the given ID"}), 404

        return jsonify({"message": "Menu item updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": "An internal error occurred"}), 500

@app.route('/api/menu_items/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
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

@app.route('/api/export_menu_items', methods=['GET'])
def export_menu_items():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT 
                mi.Name, 
                mi.Description, 
                mi.Price, 
                mi.ImageURL,
                c.CategoryName
            FROM MenuItems mi
            LEFT JOIN Category c ON mi.CategoryID = c.CategoryID
        ''')
        menu_items = cursor.fetchall()

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Menu Items", ln=True, align='C')
        pdf.ln(10)

        for item in menu_items:
            pdf.set_font("Arial", 'B', size=12)
            pdf.cell(0, 10, f"Name: {item['Name']}", 0, 1)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Description: {item['Description']}", 0, 1)
            pdf.cell(0, 10, f"Price: ${item['Price']:.2f}", 0, 1)
            pdf.cell(0, 10, f"Category: {item['CategoryName']}", 0, 1)

        # Save PDF
        pdf_file = os.path.join(app.config['UPLOAD_FOLDER'], "menu_items.pdf")
        pdf.output(pdf_file)
        return send_file(pdf_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
