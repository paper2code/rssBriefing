from flask import Blueprint, g, render_template, request

from rssbriefing import db
from rssbriefing.auth import login_required
from rssbriefing.db_utils import get_feedlist_for_dropdown, get_user_by_id
from rssbriefing.models import Briefing
from rssbriefing.email import send_standard_briefing
from rssbriefing.briefing_utils import get_standard_briefing

bp = Blueprint('briefing', __name__)


def get_latest_briefing_date(user):
    datetime_obj = db.session.query(
        db.func.max(Briefing.briefing_created)). \
        filter(Briefing.user_id == user). \
        scalar()

    return datetime_obj


def get_briefing_items(user, briefing_date):
    items = Briefing.query. \
        filter(Briefing.user_id == user). \
        filter(Briefing.briefing_created == briefing_date). \
        all()

    return items


def get_feedlist_for_logged_in_user():
    if g.user:
        feedlist = get_feedlist_for_dropdown(g.user.id)
    else:
        feedlist = None

    return feedlist


@bp.route('/')
@login_required
def index():
    # Get the date of the most recent briefing
    latest_briefing_date = get_latest_briefing_date(user=1)

    # Get all items of most recent briefing
    items = get_briefing_items(user=1, briefing_date=latest_briefing_date)

    if all([item.guid for item in items]):
        items = sorted(items, key=lambda item: int(item.guid), reverse=False)

    # If briefing available: Convert briefing date to custom string format for display
    if latest_briefing_date:
        latest_briefing_date = latest_briefing_date.strftime("%B %d, %Y at %I:%M %p")

    # Get all feeds of user for the dropdown in the header navbar
    feeds = get_feedlist_for_dropdown(g.user.id)

    send_email = request.args.get('email', None)
    if send_email:
        send_standard_briefing(user=get_user_by_id(g.user.id))

    return render_template('briefing/index.html',
                           items=items,
                           feeds=feeds,
                           briefing_date=latest_briefing_date)


@bp.route('/start')
def landing_page():
    # Get the date of the most recent briefing
    latest_briefing_date = get_latest_briefing_date(user=1)

    # Convert briefing date to custom string format for display
    latest_briefing_date = latest_briefing_date.strftime("%B %d, %Y at %I:%M %p") if latest_briefing_date else None

    # For logged in user: Get all feeds of user for the dropdown in the header navbar
    feeds = get_feedlist_for_logged_in_user()

    return render_template('landing_page/start.html',
                           feeds=feeds,
                           briefing_date=latest_briefing_date)


@bp.route('/example')
def example_briefing():

    briefing_items, latest_briefing_date = get_standard_briefing()

    # For logged in user: Get all feeds of user for the dropdown in the header navbar
    feeds = get_feedlist_for_logged_in_user()

    return render_template('landing_page/example_briefing.html',
                           items=briefing_items,
                           feeds=feeds,
                           briefing_date=latest_briefing_date)


@bp.route('/how_it_works')
def how_it_works():
    # For logged in user: Get all feeds of user for the dropdown in the header navbar
    feeds = get_feedlist_for_logged_in_user()

    return render_template('landing_page/how_it_works.html',
                           feeds=feeds)
