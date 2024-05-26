from flask import Flask, abort, render_template, redirect, url_for, flash, request
from forms import CreatePlayerForm, ChangePlayerLevel
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)


# create database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")

# Create the extension
db = SQLAlchemy(model_class=Base)
# Initialise the app with the extension
db.init_app(app)


class Players(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    family_name: Mapped[str] = mapped_column(String(250), nullable=False)
    level: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


# create the 2 team with the level of the player in the Table
def create_balanced_lists(list_1):
    sorted_list = sorted(list_1, reverse=True)

    list_2 = []
    list_3 = []

    sum_2 = 0
    sum_3 = 0

    for item in sorted_list:
        if sum_2 <= sum_3:
            list_2.append(item)
            sum_2 += item
        else:
            list_3.append(item)
            sum_3 += item

    return list_2, list_3


@app.route("/", methods=["GET", "POST"])
def home():
    form = CreatePlayerForm()
    if form.validate_on_submit():
        level = form.level.data
        result = db.session.execute(db.select(Players).where(Players.level == level))
        player = result.scalar()
        if player:
            flash("Ce niveau est déja utilisé par un autre joueur")
            return redirect(url_for('home'))
        elif level > 1000:
            flash("Votre niveau de jeu est trop haut il doit être inférieur 1000")
            return redirect(url_for('home'))
        elif level < 1:
            flash("Votre niveau de jeu est trop bas il doit être supérieur a 1")
            return redirect(url_for('home'))
        else:
            new_player = Players(
                name=form.name.data,
                family_name=form.family_name.data,
                level=form.level.data
            )
            db.session.add(new_player)
            db.session.commit()
            return redirect(url_for('show_players'))
    return render_template("index.html", form=form)


@app.route("/joueurs")
def show_players():
    result = db.session.execute(db.select(Players))
    player = result.scalars().all()
    return render_template("players.html", all_players=player)


@app.route("/equipes")
def create_team():
    # take all the table
    result = db.session.execute(db.select(Players))
    player = result.scalars().all()
    # know the number of player in the table
    number_of_player = len(player)
    # create the list with the level of all the player
    list_of_level = []
    # add the level into the list
    for i in range(number_of_player):
        lvl_player = player[i].level
        list_of_level.append(lvl_player)
    team_1, team_2 = create_balanced_lists(list_of_level)
    # know the level of each team
    level_team_1 = sum(team_1)
    level_team_2 = sum(team_2)
    # know the number of player in each team
    number_of_player_team_1 = len(team_1)
    number_of_player_team_2 = len(team_2)
    # create the 2 last list that are going to take the name family name and the level of each player in each team
    team_1_sql = []
    team_2_sql = []
    # add the information in the list
    for i in range(number_of_player_team_1):
        result_1 = db.session.execute(db.select(Players).where(Players.level == team_1[i]))
        player_1 = result_1.scalars().all()
        team_1_sql.append(player_1)
    for i in range(number_of_player_team_2):
        result_2 = db.session.execute(db.select(Players).where(Players.level == team_2[i]))
        player_2 = result_2.scalars().all()
        team_2_sql.append(player_2)
    # send the information into the html
    return render_template('team.html', team_1_sql=team_1_sql, team_2_sql=team_2_sql, level_team_1=level_team_1,
                           level_team_2=level_team_2)


@app.route("/nouveau-niveau", methods=["GET", "POST"])
def update_level():
    form = ChangePlayerLevel()
    player_id = request.args.get("id")
    # player where we want to change his level
    player = db.get_or_404(Players, player_id)
    if form.validate_on_submit():
        # level in form
        level = form.level.data
        # is there player with this level
        result = db.session.execute(db.select(Players).where(Players.level == level))
        actual_player = result.scalar()
        if actual_player:
            flash("Ce niveau est déja utilisé par un autre joueur.")
            return render_template("update_level.html", form=form)
        elif level > 1000:
            flash("Votre niveau de jeu est trop haut il doit être inférieur 1000.")
            return render_template("update_level.html", form=form)
        elif level < 1:
            flash("Votre niveau de jeu est trop bas il doit être supérieur a 1.")
            return render_template("update_level.html", form=form)
        else:
            player.level = level
            db.session.commit()
            return redirect(url_for("show_players"))
    return render_template("update_level.html", form=form)


@app.route('/delete')
def delete_player():
    player_id = request.args.get("id")
    player = db.get_or_404(Players, player_id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for("show_players"))


if __name__ == "__main__":
    app.run(debug=False, port=5000)
