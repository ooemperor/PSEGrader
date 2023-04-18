"""Task-related handlers for CWS.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa

import logging

import tornado.web

from cms.server import multi_contest
from cmscommon.mimetypes import get_type_for_file_name

from ..phase_management import actual_phase_required

from .contest import ContestHandler


logger = logging.getLogger(__name__)

class ExerciseOverviewHandler(ContestHandler):
    """
    Shows the data of the exercise
    specifically the tasks of the exercise in a tabular form.
    """

    @tornado.web.authenticated
    @actual_phase_required(0, 3)
    @multi_contest
    def get(self, exercise_name):
        exercise = self.get_exercise(exercise_name)
        if exercise is None:
            raise tornado.web.HTTPError(404)

        self.render("exercise.html", exercise=exercise, **self.r_params)
