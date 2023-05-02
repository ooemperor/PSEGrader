"""
Contest Exercise Handlers
@author: ooemperor
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa

from cms.db import Contest, Exercise, Task
from cmscommon.datetime import make_datetime

from .base import BaseHandler, require_permission


class ContestExercisesHandler(BaseHandler):
    REMOVE_FROM_CONTEST = "Remove from contest"
    MOVE_UP = "Move up"
    MOVE_DOWN = "Move down"

    @require_permission(BaseHandler.AUTHENTICATED)
    def get(self, contest_id):
        self.contest = self.safe_get_item(Contest, contest_id)

        self.r_params = self.render_params()
        self.r_params["contest"] = self.contest
        self.r_params["unassigned_exercises"] = \
            self.sql_session.query(Exercise)\
                .filter(Exercise.contest_id.is_(None))\
                .all()
        self.render("contest_exercises.html", **self.r_params)

    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self, contest_id):
        fallback_page = self.url("contest", contest_id, "exercises")

        self.contest = self.safe_get_item(Contest, contest_id)

        try:
            exercise_id = self.get_argument("exercise_id")
            operation = self.get_argument("operation")
            assert operation in (
                self.REMOVE_FROM_CONTEST,
                self.MOVE_UP,
                self.MOVE_DOWN
            ), "Please select a valid operation"
        except Exception as err:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(err))
            self.redirect(fallback_page)
            return

        exercise = self.safe_get_item(Exercise, exercise_id)
        exercise2 = None

        if operation == self.REMOVE_FROM_CONTEST:
            # Save the current exercise_num (position in the contest).
            exercise_num = exercise.num

            # Unassign the exercise to the contest.
            exercise.contest = None
            for task in exercise.tasks:
                task.contest = None
            exercise.num = None  # not strictly necessary

            # Decrease by 1 the num of every subsequent exercise.
            for e in self.sql_session.query(Exercise)\
                         .filter(Exercise.contest == self.contest)\
                         .filter(Exercise.num > exercise_num)\
                         .all():
                e.num -= 1

        elif operation == self.MOVE_UP:
            exercise2 = self.sql_session.query(Exercise)\
                        .filter(Exercise.contest == self.contest)\
                        .filter(Exercise.num == exercise.num - 1)\
                        .first()

        elif operation == self.MOVE_DOWN:
            exercise2 = self.sql_session.query(Exercise)\
                        .filter(Exercise.contest == self.contest)\
                        .filter(Exercise.num == exercise.num + 1)\
                        .first()

        # Swap exercise.num and exercise2.num, if needed
        if exercise2 is not None:
            tmp_a, tmp_b = exercise.num, exercise2.num
            exercise.num, exercise2.num = None, None
            self.sql_session.flush()
            exercise.num, exercise2.num = tmp_b, tmp_a

        if self.try_commit():
            # Create the exercise on RWS.
            self.service.proxy_service.reinitialize()

        # Maybe they'll want to do this again (for another exercise)
        self.redirect(fallback_page)


class AddContestExerciseHandler(BaseHandler):
    """
    Adding a exercise to a contest Handler
    """
    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self, contest_id):
        fallback_page = self.url("contest", contest_id, "exercises")

        self.contest = self.safe_get_item(Contest, contest_id)

        try:
            exercise_id = self.get_argument("exercise_id")
            # Check that the admin selected some exercise.
            assert exercise_id != "null", "Please select a valid exercise"
        except Exception as err:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(err))
            self.redirect(fallback_page)
            return

        exercise = self.safe_get_item(Exercise, exercise_id)

        # Assign the exercise to the contest.
        exercise.num = len(self.contest.exercises)
        exercise.contest = self.contest

        # adding all the tasks of the exercise as well to the contest
        for task in exercise.tasks:
            task.contest = self.contest


        if self.try_commit():
            # Create the exercise on RWS.
            self.service.proxy_service.reinitialize()

        # Maybe they'll want to do this again (for another exercise)
        self.redirect(fallback_page)
