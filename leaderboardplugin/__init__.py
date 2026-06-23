from pathlib import Path

from flask import redirect, render_template, request, url_for

from CTFd.plugins import override_template
from CTFd.utils import config
from CTFd.utils.config.visibility import scores_visible
from CTFd.utils.decorators.visibility import (
    check_account_visibility,
    check_score_visibility,
)
from CTFd.utils.helpers import get_infos
from CTFd.utils.modes import TEAMS_MODE, USERS_MODE
from CTFd.utils.scores import get_standings, get_team_standings, get_user_standings
from CTFd.utils.user import is_admin

PLUGIN_ROOT = Path(__file__).resolve().parent


def _build_standings(active_view):
    if active_view == USERS_MODE:
        raw_standings = get_user_standings()
        view_label = "Solo"
    elif active_view == TEAMS_MODE:
        raw_standings = get_team_standings()
        view_label = "Team"
    else:
        raw_standings = get_standings()
        view_label = "Solo"

    standings = []
    for index, row in enumerate(raw_standings, start=1):
        if active_view == USERS_MODE:
            account_id = row.user_id
            account_url = url_for("users.public", user_id=account_id)
        else:
            account_id = row.team_id if hasattr(row, "team_id") else row.account_id
            account_url = url_for("teams.public", team_id=account_id)

        standings.append(
            {
                "pos": index,
                "account_id": account_id,
                "account_url": account_url,
                "name": row.name,
                "score": int(row.score),
            }
        )
    return standings, view_label


@check_account_visibility
@check_score_visibility
def leaderboard_listing():
    infos = get_infos()
    requested_view = request.args.get("view")
    active_view = requested_view if requested_view in {TEAMS_MODE, USERS_MODE} else USERS_MODE

    if config.is_scoreboard_frozen():
        infos.append("Scoreboard has been frozen")

    if is_admin() is True and scores_visible() is False:
        infos.append("Scores are not currently visible to users")

    standings, view_label = _build_standings(active_view)

    return render_template(
        "scoreboard.html",
        infos=infos,
        active_view=active_view,
        view_label=view_label,
        standings=standings,
    )


def legacy_listing():
    view = request.args.get("view")
    if view in {TEAMS_MODE, USERS_MODE}:
        return redirect(url_for("scoreboard.listing", view=view), code=301)
    return redirect(url_for("scoreboard.listing", view=USERS_MODE), code=301)


def extra_leaderboard_route():
    return redirect(url_for("scoreboard.listing", view=request.args.get("view", USERS_MODE)))


def load(app):
    template = (PLUGIN_ROOT / "templates" / "scoreboard.html").read_text()
    override_template("scoreboard.html", template)

    if "scoreboard.listing" in app.view_functions:
        app.view_functions["scoreboard.listing"] = leaderboard_listing

    if "scoreboard.legacy_listing" in app.view_functions:
        app.view_functions["scoreboard.legacy_listing"] = legacy_listing

    if "leaderboardplugin.listing" not in app.view_functions:
        app.add_url_rule("/leaderboard", "leaderboardplugin.listing", leaderboard_listing)

