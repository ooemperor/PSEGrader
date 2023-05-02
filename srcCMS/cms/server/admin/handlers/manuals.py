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


class ManualsHandler(BaseHandler):
    """
    Handler for the manuals Page
    """

    @require_permission(BaseHandler.AUTHENTICATED)
    def get(self):
        """
        Rendering the manuals page
        :return: No return statement.
        """
        self.r_params = self.render_params()
        self.render("manuals.html", **self.r_params)
