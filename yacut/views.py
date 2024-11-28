from random import choices
import re

from flask import flash, redirect, render_template

from . import app, db
from .forms import URLMapForm
from .models import URLMap


CHOICE_STRING = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 'abcdefghijklmnopqrstuvwxyz'
                 '0123456789')

VALID_SHORT_URL_PATTERN = re.compile(r'^[A-Za-z0-9]{1,16}$')
MAX_LENGTH_OF_SHORT_URL = 6


def get_unique_short_id():
    """Генерирует уникальный короткий идентификатор."""
    while True:
        short_url = ''.join(choices(CHOICE_STRING, k=MAX_LENGTH_OF_SHORT_URL))
        if URLMap.query.filter_by(short=short_url).first() is None:
            return short_url


def is_valid_short_url(short_url):
    """Проверяет валидность короткого идентификатора."""
    return bool(VALID_SHORT_URL_PATTERN.match(short_url))


@app.route('/', methods=['GET', 'POST'])
def index_view():
    """Обрабатывает GET и POST запросы на главной странице."""
    form = URLMapForm()
    if form.validate_on_submit():
        short_url = form.custom_id.data or get_unique_short_id()
        if URLMap.query.filter_by(short=short_url).first() is not None:
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('urlmap.html', form=form)
        if not is_valid_short_url(short_url):
            flash('URL содержит недопустимые символы')
            return render_template('urlmap.html', form=form)
        urlmap = URLMap(
            original=form.original_link.data,
            short=short_url
        )
        db.session.add(urlmap)
        db.session.commit()
        return render_template('urlmap.html', form=form, urlmap=urlmap)
    return render_template('urlmap.html', form=form)


@app.route('/<string:short_url>', methods=['GET'])
def redirect_view(short_url):
    """Перенаправляет пользователя на оригинальный URL."""
    urlmap = URLMap.query.filter_by(short=short_url).first_or_404()
    original_url = urlmap.original
    return redirect(original_url)
