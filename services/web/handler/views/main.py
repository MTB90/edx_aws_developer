import logging
import socket

from flask import Blueprint, render_template, jsonify, request

from factories import cq_factory
from photorec.use_cases.get_health_service import GetHealthService
from photorec.use_cases.photos.get_photos import GetPhotosQuery
from photorec.use_cases.tag.get_all_tags import GetAllTagsQuery

blueprint = Blueprint('main', __name__)
log = logging.getLogger(__name__)


@blueprint.route('/')
def index():
    """Homepage route"""
    container = socket.gethostname()

    service = "api"
    use_case = cq_factory.get(GetHealthService)
    health = use_case.execute(service)

    return render_template("index.html", container=container, service=service, health=health)


@blueprint.route('/top')
def top():
    """Top photos"""
    tag = request.args.get('tag')
    query = None if tag is None else {'tag': tag}

    use_case = cq_factory.get(GetAllTagsQuery)
    tags = use_case.execute()

    use_case = cq_factory.get(GetPhotosQuery)
    photos = use_case.execute(query=query)

    return render_template("top.html", tags=tags, photos=photos)


@blueprint.route('/health')
def health():
    return jsonify({
        'status': 'running',
        'container': socket.gethostname()
    })
