from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class CreatePlayerForm(FlaskForm):
    name = StringField("Prénom", validators=[DataRequired()])
    family_name = StringField("Nom", validators=[DataRequired()])
    level = IntegerField("Niveau de jeu (0-1000)", validators=[DataRequired()])
    submit = SubmitField("Ajouter un joueur")


class ChangePlayerLevel(FlaskForm):
    level = IntegerField("Nouveau niveau de jeu (0-1000)", validators=[DataRequired()])
    submit = SubmitField("Ajouter ce niveau de jeu")
