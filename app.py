from flask import Flask, render_template
from flask_babel import Babel, gettext

app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(app)

@babel.localeselector
def get_locale():
    return 'fr'  # tu peux changer après pour gérer l’auto-détection

@app.route('/')
def home():
    return render_template('home.html', title=gettext("Accueil"))

@app.route('/about')
def about():
    return render_template('about.html', title=gettext("À propos"))

if __name__ == '__main__':
    app.run(debug=True)
