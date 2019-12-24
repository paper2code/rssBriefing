from flask import Blueprint, g, render_template

from donkey_package import db
from donkey_package.auth import login_required
from donkey_package.db_utils import get_feedlist_for_dropdown
from donkey_package.models import Briefing

bp = Blueprint('briefing', __name__)


@bp.route('/')
@login_required
def index():

    latest_briefing_date = db.session.query(
        db.func.max(Briefing.briefing_created)). \
        filter(Briefing.user_id == g.user.id).scalar()

    items = Briefing.query. \
        filter(Briefing.user_id == g.user.id). \
        filter(Briefing.briefing_created == latest_briefing_date). \
        all()

    feeds = get_feedlist_for_dropdown(g.user.id)

    return render_template('briefing/index.html', items=items, feeds=feeds, briefing_date=latest_briefing_date)
