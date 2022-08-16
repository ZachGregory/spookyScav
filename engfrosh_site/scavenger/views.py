from typing import Optional, Union
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render  # noqa F401

from common_models.models import Puzzle, Team
from django.contrib.auth.decorators import login_required, permission_required

import logging

logger = logging.getLogger("engfrosh_site.scavenger.views")


@login_required(login_url='/accounts/login')
def index(request: HttpRequest) -> HttpResponse:

    team = Team.from_user(request.user)
    if not team:
        return render(request, "scavenger_index.html", context={"team": None})

    active_puzzles = team.active_puzzles
    completed_puzzles = team.completed_puzzles
    logger.debug(f"{[p.name for p in active_puzzles]}")

    context = {
        "team": team,
        # "puzzles": team.active_puzzles
        "active_puzzles": active_puzzles,
        "completed_puzzles": completed_puzzles
    }

    return render(request, "scavenger_index.html", context=context)


@login_required(login_url='/accounts/login')
def puzzle_view(request: HttpRequest, slug: str) -> HttpResponse:
    # TODO add support for lockouts
    # TODO add permission verification

    team = Team.from_user(request.user)
    if not team:
        return HttpResponse("Sorry you aren't on a team. If this is incorrect, please contact supoort")

    try:
        puz: Union[Puzzle, None] = Puzzle.objects.get(secret_id=slug)
    except Puzzle.DoesNotExist:
        puz = None

    if not (puz and puz.is_viewable_for_team(team)):
        return HttpResponse("You do not have access to this puzzle.")

    context = {
        "puzzle": puz,
        "view_only": puz.is_completed_for_team(team)
    }

    return render(request, "scavenger_question.html", context)
