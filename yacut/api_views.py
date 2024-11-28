from http import HTTPStatus

from flask import jsonify, request, url_for

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id, is_valid_short_url


@app.route('/api/id/', methods=['POST'])
def add_url():
    """Создает короткую ссылку и сохраняет в базе данных."""
    raw_data = request.data
    if raw_data == b'':
        raise InvalidAPIUsage('Отсутствует тело запроса')

    data = request.get_json()
    if not data.get('url'):
        raise InvalidAPIUsage('"url" является обязательным полем!')

    short = data.get('custom_id') or get_unique_short_id()
    if URLMap.query.filter_by(short=short).first() is not None:
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.')
    if not is_valid_short_url(short):
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')

    urlmap = URLMap(
        original=data.get('url'),
        short=short
    )
    db.session.add(urlmap)
    db.session.commit()

    return jsonify({
        'url': urlmap.original,
        'short_link': url_for(
            'redirect_view', short_url=urlmap.short, _external=True)
    }), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_url(short_id):
    """Получение оригинального URL по короткому идентификатору."""
    urlmap = URLMap.query.filter_by(short=short_id).first()
    if urlmap is not None:
        return jsonify({'url': urlmap.original}), HTTPStatus.OK
    raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
