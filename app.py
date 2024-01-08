from flask import Flask, render_template, jsonify, request
import requests 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pokedex.sqlite"

db = SQLAlchemy(app)

class Pokemon(db.Model):
    id:Mapped[int] = mapped_column(db.Integer, primary_key=True,autoincrement=True)
    name:Mapped[str]= mapped_column(db.String,nullable=False)
    height:Mapped[float] = mapped_column(db.Float,nullable=False)
    weight: Mapped[float] = mapped_column(db.Float, nullable=False)
    order: Mapped[int] = mapped_column(db.Integer,nullable=False)
    type :Mapped[str]= mapped_column(db.String,nullable=False)

with app.app_context():
    db.create_all()

def get_pokemon_data(pokemon):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon}'
    r = requests.get(url).json()
    return r

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        pokemon_name = request.form['pokemon_name']
        return search_pokemon(pokemon_name)

    return render_template('pokemon.html', pokemon=None)

@app.route("/pokemon/<name>")
def search_pokemon(name):
    data = get_pokemon_data(name.lower())
    if 'sprites' not in data or 'official-artwork' not in data['sprites']['other']:
        return render_template('pokemon.html', pokemon=None)
    
    official_artwork = data['sprites']['other'].get('official-artwork', {}).get('front_default')
    dream_artwork = data['sprites']['other'].get('dream-artwork', {}).get('front_default')

    if not official_artwork:
        return render_template('pokemon.html', pokemon=None)

    pokemon = {
        'name': data['name'].upper(),
        'height': data['height'],
        'weight': data['weight'],
        'order': data['order'],
        'type': 'Estudiante',
        'hp': data.get('stats')[0].get('base_stat'),
        'attack': data.get('stats')[1].get('base_stat'),
        'defence': data.get('stats')[2].get('base_stat'),
        'speed': data.get('stats')[5].get('base_stat'),
        'photo': official_artwork,
        'photo1': dream_artwork if dream_artwork else ''  
    }

    return render_template('pokemon.html', pokemon=pokemon)

@app.route("/detalle/<hp>/<attack>/<defence>/<speed>/")
def detalle(hp,attack,defence,speed):
    return render_template('detalle.html',hp = hp, attack = attack, defence = defence, speed = speed)


@app.route("/insert_pokemon/<pokemon>")
def insert(pokemon):
    new_pokemon = pokemon
    if new_pokemon:
         obj = Pokemon(pokemon)
         db.session.add(obj)
         db.session.commit()
    return 'Pokemon Agregado'

@app.route("/select")
def select():
    lista_pokemon= Pokemon.query.all()
    for p in lista_pokemon:
        print(p.name)
    return 'alo'

@app.route("/selectbyname/<name>")
def selectbyname(name):
    poke= Pokemon.query.filter_by(name=name).first()
    return str(poke.id),str(poke.name)

@app.route("/selectbyid/<id>")
def selectbyid(id):
    poke = Pokemon.query.filter_by(id=id).first()
    return str(poke.id) + str(poke.name)

@app.route("/deletetbyid/<id>")
def deletetbyid(id):
    pokemon_a_eliminar = Pokemon.query.filter_by(id=id).first()
    db.session.delete(pokemon_a_eliminar)
    db.session.commit()
    return 'Pokemon Eliminado'

if __name__=='__main__':
    app.run(debug=True)