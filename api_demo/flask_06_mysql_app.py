from flask import Flask, jsonify
from flask_06_db_config import get_mysql_connection
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Flask App using MySQL",
    description="A simple API to demonstrate the power of RestAPI with MySQL",
)

# Establish database connection
mysql_conn = get_mysql_connection()


# -------------------------
# Home Route
# -------------------------
@api.route("/", methods=["GET"])
class Sakila(Resource):
    def get(self):
        """Load HomePage."""
        return jsonify("Welcome to Sakila Database")


# -------------------------
# API MODELS
# -------------------------
film_model = api.model(
    "FilmModel",
    {
        "film_id": fields.Integer(description="Film ID", required=True, example=2),
    },
)

film_actor_model = api.model(
    "FilmActorModel",
    {
        "film_id": fields.Integer(description="Film ID", required=True, example=2),
    },
)

film_inventory_model = api.model(
    "FilmInventoryModel",
    {
        "film_id": fields.Integer(description="Film ID", required=True, example=2),
    },
)


# -------------------------
# Film Details Route
# -------------------------
@api.route("/film/<int:film_id>", methods=["GET"])
class Film(Resource):
    @api.doc(model=[film_model])
    def get(self, film_id):
        """Retrieve film details by film ID."""
        with mysql_conn.cursor() as cursor:
            sql = """
            SELECT title, description, release_year
            FROM film
            WHERE film_id = %s
            """
            cursor.execute(sql, (film_id,))
            result = cursor.fetchone()

            if not result:
                return jsonify({"message": "Film not found"}), 404

            film_data = {
                "title": result[0],
                "description": result[1],
                "release_year": result[2],
            }

        return jsonify({"film": film_data})


# -------------------------
# Film Actors Route
# -------------------------
@api.route("/film/<int:film_id>/actors", methods=["GET"])
class FilmActor(Resource):
    @api.doc(model=[film_actor_model])
    def get(self, film_id):
        """Retrieve all actors for a given film."""
        actors_data = []

        with mysql_conn.cursor() as cursor:
            actor_query = """
            SELECT a.actor_id, a.first_name, a.last_name
            FROM actor a
            JOIN film_actor fa ON a.actor_id = fa.actor_id
            WHERE fa.film_id = %s
            """
            cursor.execute(actor_query, (film_id,))
            actors = cursor.fetchall()

            for actor in actors:
                actor_id, first_name, last_name = actor

                other_films_query = """
                SELECT f.film_id, f.title
                FROM film f
                JOIN film_actor fa ON f.film_id = fa.film_id
                WHERE fa.actor_id = %s AND f.film_id != %s
                """
                cursor.execute(other_films_query, (actor_id, film_id))
                other_films = cursor.fetchall()

                actors_data.append(
                    {
                        "actor_id": actor_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "other_films": other_films,
                    }
                )

        return jsonify({"actors": actors_data})


# -------------------------
# Film Inventory Route (HW Requirement)
# -------------------------
@api.route("/film/<int:film_id>/inventory", methods=["GET"])
class FilmInventory(Resource):
    @api.doc(model=[film_inventory_model])
    def get(self, film_id):
        """Retrieve all inventory (inventory ID, store ID, last update) for a given film."""
        inventory_data = []

        with mysql_conn.cursor() as cursor:

            # Problem 1(b)
            inventory_query = """
            SELECT inv.inventory_id, inv.store_id, inv.last_update
            FROM inventory inv
            JOIN film fi ON inv.film_id = fi.film_id
            WHERE fi.film_id = %s
            """
            cursor.execute(inventory_query, (film_id,))
            inventory = cursor.fetchall()

            # Problem 1(c)
            films_query = """
            SELECT f.title
            FROM film f
            JOIN inventory fi ON f.film_id = fi.film_id
            WHERE fi.film_id = %s
            """
            cursor.execute(films_query, (film_id,))
            film = cursor.fetchone()

            if not film:
                return jsonify({"message": "Film not found"}), 404

            film_title = film[0]

            # Problem 1(d)
            for inv in inventory:
                inventory_data.append(
                    {
                        "inventory_id": inv[0],
                        "store_id": inv[1],
                        "last_update": str(inv[2]),
                        "film_title": film_title,
                    }
                )

        return jsonify({"inventory": inventory_data})


# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)