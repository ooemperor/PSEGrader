"""
Exercise related Handlers for the admin panel.
@author: ooemperor
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa
from six import itervalues

import logging
import traceback

import tornado.web

from cms.db import Attachment, Dataset, Session, Exercise
from cms.util import string_formatting
from cmscommon.datetime import make_datetime

from .base import BaseHandler, SimpleHandler, require_permission

logger = logging.getLogger(__name__)


class ExerciseHandler(BaseHandler):
    """
    The Handler for a given Exercise.
    """
    @require_permission(BaseHandler.AUTHENTICATED)
    def get(self, exercise_id):
        """
        Getting all the values for a given Exercise
        :param exercise_id:
        :return: No return statement.
        """
        exercise = self.safe_get_item(Exercise, exercise_id)
        self.r_params = self.render_params()
        self.r_params["exercise"] = exercise
        self.render("exercise.html", **self.r_params)

    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self, exercise_id):
        """
        Updating the given exercise
        :param exercise_id: the id of the exercise for a unique identification
        :return: Empty return (not even None)
        """

        exercise = self.safe_get_item(Exercise, exercise_id)

        try:
            # getting the values from the html file.
            attrs = exercise.get_attrs()
            self.get_string(attrs, "name", empty=None)
            attrs["name"] = string_formatting(attrs["name"])
            self.get_string(attrs, "title")
            self.get_string(attrs, "exercise_tags", empty=None)

            assert attrs.get("name") is not None, "No Exercise name specified"
            exercise.set_attrs(attrs)

        except Exception as err:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(err))
            self.redirect(self.url("exercise", exercise_id))
            return

        if self.try_commit():
            # Update the exercise and score on RWS.
            self.service.proxy_service.dataset_updated(
                exercise_id=exercise.id)
        self.redirect(self.url("exercise", exercise_id))


class ExerciseListHandler(SimpleHandler("exercises.html")):
    """
    The handler for the list of all exercises.
    """
    REMOVE = "Remove"

    @require_permission(BaseHandler.AUTHENTICATED)
    def post(self):
        exercise_id = self.get_argument("exercise_id")
        operation = self.get_argument("operation")

        if operation == self.REMOVE:
            asking_page = self.url("exercise", exercise_id, "remove")
            # Open asking for remove page
            self.redirect(asking_page)
        else:
            self.service.add_notification(
                make_datetime(), "Invalid operation %s" % operation, "")
            self.redirect(self.url("exercises"))


class AddExerciseHandler(SimpleHandler("add_exercise.html", permission_all=True)):
    """
    Handler for adding a exercise in the admin panel.
    """
    @require_permission(BaseHandler.PERMISSION_ALL)
    def post(self):
        """
        posting the values to add a new exercise
        :return: a blank return (not even None)
        """
        fallback_page = self.url("exercises", "add")

        try:
            # getting values from template
            attrs = dict()
            self.get_string(attrs, "name", empty=None)
            attrs["name"] = string_formatting(attrs["name"])
            assert attrs.get("name") is not None, "No exercise name specified."
            self.get_string(attrs, "title", empty=None)
            if attrs.get("title") is None:
                attrs["title"] = attrs["name"]
            self.get_string(attrs, "exercise_tags", empty="")

            # Constructing the exercise and then adding to DB
            exercise = Exercise(**attrs)
            self.sql_session.add(exercise)

        except Exception as err:
            self.service.add_notification(
                make_datetime(), "Invalid field(s)", repr(err))
            self.redirect(fallback_page)

        if self.try_commit():
            self.service.proxy_service.reinitialize()
            self.redirect(self.url("exercise", exercise.id))
        else:
            self.redirect(fallback_page)


class RemoveExerciseHandler(BaseHandler):
    """
    Sending the admin user to the remove page. If yes, then
    """

    @require_permission(BaseHandler.PERMISSION_ALL)
    def get(self, exercise_id):
        exercise = self.safe_get_item(Exercise, exercise_id)

        self.r_params = self.render_params()
        self.r_params["exercise"] = exercise
        self.render("exercise_remove.html", **self.r_params)

    @require_permission(BaseHandler.PERMISSION_ALL)
    def delete(self, exercise_id):
        exercise = self.safe_get_item(Exercise, exercise_id)
        contest_id = exercise.contest_id
        num = exercise.num

        self.sql_session.delete(exercise)
        # Keeping the exercises nums to the range 0... n - 1.
        if contest_id is not None:
            following_exercises = self.sql_session.query(Exercise) \
                .filter(Exercise.contest_id == contest_id) \
                .filter(Exercise.num > num) \
                .all()
            for exercise in following_exercises:
                exercise.num -= 1
        if self.try_commit():
            self.service.proxy_service.reinitialize()

        # Maybe they'll want to do this again (for another exercise)
        self.write("../../exercises")
