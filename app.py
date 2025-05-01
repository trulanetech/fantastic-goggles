from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Connect to (or create) a simple database
conn = sqlite3.connect('recipes.db', check_same_thread=False)
cursor = conn.cursor()

# Create a recipes table if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    ingredients TEXT,
    instructions TEXT,
    cook_time_minutes INTEGER,
    cuisine TEXT,
    tags TEXT
)
''')
conn.commit()

# Upload a new recipe
@app.route('/upload_recipe', methods=['POST'])
def upload_recipe():
    data = request.get_json()
    cursor.execute('''
        INSERT INTO recipes (name, ingredients, instructions, cook_time_minutes, cuisine, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        str(data['ingredients']),
        str(data['instructions']),
        data['cook_time_minutes'],
        data['cuisine'],
        str(data['tags'])
    ))
    conn.commit()
    return jsonify({"status": "success"})

# Search for recipes
@app.route('/search_recipes', methods=['GET'])
def search_recipes():
    ingredient = request.args.get('ingredient', '')
    max_cook_time = request.args.get('max_cook_time')

    query = f"SELECT id, name, cook_time_minutes FROM recipes WHERE ingredients LIKE '%{ingredient}%'"
    if max_cook_time:
        query += f" AND cook_time_minutes <= {max_cook_time}"

    results = cursor.execute(query).fetchall()

    # Format results nicely
    recipes = []
    for r in results:
        recipes.append({
            "id": r[0],
            "name": r[1],
            "cook_time_minutes": r[2]
        })

    return jsonify(recipes)

# Get full recipe by ID
@app.route('/get_recipe', methods=['GET'])
def get_recipe():
    recipe_id = request.args.get('recipe_id')
    result = cursor.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()

    if result:
        recipe = {
            "id": result[0],
            "name": result[1],
            "ingredients": result[2],
            "instructions": result[3],
            "cook_time_minutes": result[4],
            "cuisine": result[5],
            "tags": result[6]
        }
        return jsonify(recipe)
    else:
        return jsonify({"error": "Recipe not found"}), 404

# Home page (optional, just to prove it's live)
@app.route('/')
def home():
    return "TasteAPI is running!"

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
