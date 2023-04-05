

"""Task-related handlers for AWS for a specific exercise.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa

from cms.db import Contest, Task, Exercise
from cmscommon.datetime import make_datetime

from .base import BaseHandler, require_permission


class ExerciseTasksHandler(BaseHandler):
    REMOVE_FROM_EXERCISE = "Remove from exercise"
    MOVE_UP = "Move up"
    MOVE_DOWN = "Move down"

    @require_permission(BaseHandler.AUTHENTICATED)
    def get(self, exercise_id):
        self.contest = self.safe_get_item(Exercise, exercise_id)

        self.r_params = self.render_params()
        self.r_params["exercise"] = self.exercise
        self.r_params["unassigned_tasks"] = \
            self.sql_session.query(Task)\
                .filter(Task.exercise_id.is_(None))\
                .all()
        self.render("exercise_tasks.html", **self.r_params)


    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self, exercise_id):
        fallback_page = self.url("exercise", exercise_id, "tasks")

        self.exercise = self.safe_get_item(Exercise, exercise_id)

        try:
            task_id = self.get_argument("task_id")
            operation = self.get_argument("operation")
            assert operation in (
                self.REMOVE_FROM_EXERCISE,
                self.MOVE_UP,
                self.MOVE_DOWN
            ), "Please select a valid operation"
        except Exception as error:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(error))
            self.redirect(fallback_page)
            return

        task = self.safe_get_item(Task, task_id)
        task2 = None

        if operation == self.REMOVE_FROM_CONTEST:
            # Save the current task_num (position in the contest).
            task_num = task.num

            # Unassign the task to the contest.
            task.exercise = None
            task.num = None  # not strictly necessary

            # Decrease by 1 the num of every subsequent task.
            for t in self.sql_session.query(Task)\
                         .filter(Task.exercise == self.exercise)\
                         .filter(Task.num > task_num)\
                         .all():
                t.num -= 1

        elif operation == self.MOVE_UP:
            task2 = self.sql_session.query(Task)\
                        .filter(Task.exercise == self.exercise)\
                        .filter(Task.num == task.num - 1)\
                        .first()

        elif operation == self.MOVE_DOWN:
            task2 = self.sql_session.query(Task)\
                        .filter(Task.exercise == self.exercise)\
                        .filter(Task.num == task.num + 1)\
                        .first()

        # Swap task.num and task2.num, if needed
        if task2 is not None:
            tmp_a, tmp_b = task.num, task2.num
            task.num, task2.num = None, None
            self.sql_session.flush()
            task.num, task2.num = tmp_b, tmp_a

        if self.try_commit():
            # Create the user on RWS.
            self.service.proxy_service.reinitialize()

        # Maybe they'll want to do this again (for another task)
        self.redirect(fallback_page)


class AddExerciseTasksHandler(BaseHandler):
    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self, exercise_id):
        fallback_page = self.url("contest", exercise_id, "tasks")

        self.exercise = self.safe_get_item(Exercise, exercise_id)

        try:
            task_id = self.get_argument("task_id")
            # Check that the admin selected some task.
            assert task_id != "null", "Please select a valid task"
        except Exception as err:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(err))
            self.redirect(fallback_page)
            return

        task = self.safe_get_item(Task, task_id)

        # Assign the task to the contest.
        task.num = len(self.exercise.tasks)
        task.exercise = self.exercise

        if self.try_commit():
            # Create the user on RWS.
            self.service.proxy_service.reinitialize()

        # Maybe they'll want to do this again (for another task)
        self.redirect(fallback_page)
