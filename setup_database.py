import sqlite3
from datetime import datetime

def create_tables(cursor):
    # Create Category Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Category (
        CategoryID INTEGER PRIMARY KEY,
        CategoryName TEXT NOT NULL,
        Description TEXT,
        CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        ModifiedDate DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Menu Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS MenuItems (
        MenuItemID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Description TEXT,
        Price DECIMAL(10, 2) NOT NULL,
        CategoryID INTEGER,
        AvailabilityStatus BOOLEAN DEFAULT 1,
        ImageURL TEXT,
        CreatedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        ModifiedDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
    )
    ''')

def insert_sample_data(cursor):
    # Insert sample categories
    categories = [
        ("Main Course", "Primary dish of a meal"),
        ("Appetizer", "Small dish served before the main course"),
        ("Dessert", "Sweet course at the end of a meal"),
        ("Beverage", "Drinks to accompany the meal")
    ]
    cursor.executemany("INSERT INTO Category (CategoryName, Description) VALUES (?, ?)", categories)

    # Insert sample menu items
    menu_items = [
        ("Margherita Pizza", "Classic pizza with tomato, mozzarella, and basil", 12.99, 1, 1, "/static/images/margherita.jpg"),
        ("Caesar Salad", "Romaine lettuce with Caesar dressing and croutons", 8.99, 2, 1, "/static/images/caesar_salad.jpg"),
        ("Chocolate Lava Cake", "Warm chocolate cake with a gooey center", 6.99, 3, 1, "/static/images/lava_cake.jpg"),
        ("Iced Tea", "Freshly brewed and chilled black tea", 2.99, 4, 1, "/static/images/iced_tea.jpg")
    ]
    cursor.executemany("INSERT INTO MenuItems (Name, Description, Price, CategoryID, AvailabilityStatus, ImageURL) VALUES (?, ?, ?, ?, ?, ?)", menu_items)

# Connect to the database (this will create it if it doesn't exist)
conn = sqlite3.connect('enhanced_menu_management.db')
cursor = conn.cursor()

# Create tables
create_tables(cursor)

# Insert sample data
insert_sample_data(cursor)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database setup complete with sample data.")
