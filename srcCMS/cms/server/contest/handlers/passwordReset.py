#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Password-related handlers for CWS for a specific task.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa

import logging
import re

import tornado.web

from cms import config
from cms.db import UserTest, UserTestResult, User
from cms.grading.languagemanager import get_language
from cms.server import multi_contest
from cms.server.contest.submission import get_submission_count, \
    TestingNotAllowed, UnacceptableUserTest, accept_user_test
from cmscommon.crypto import encrypt_number, hash_password
from cmscommon.mimetypes import get_type_for_file_name

from ..phase_management import actual_phase_required

from .contest import ContestHandler, FileHandler


logger = logging.getLogger(__name__)


# Dummy function to mark translatable strings.
def N_(msgid):
    return msgid


class PasswordResetHandler(ContestHandler):
    """
    Serves the password Reset interface

    """
    @multi_contest
    def get(self):
        self.render("password_reset.html", **self.r_params)

    def post(self, user):
        fallback_page = self.contest_url()

        try:
            user = self.current_user
            new_password = self.get_argument("password_1", "")

            user.password = hash_password(new_password, "bcrypt")
            self.sql_session.commit()


        except Exception as error:
            self.redirect(fallback_page)
            return

        self.redirect(fallback_page)
