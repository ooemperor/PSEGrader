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
import random
import string
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
from mail import sendMailNoAuth


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

    def post(self, arg):
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


class PasswordForgottenHandler(ContestHandler):
    """
        Handler for Forgotten Password which regenerates a new password.
    """
    @multi_contest
    def get(self):
        self.render("password_forgotten.html", **self.r_params)

    def post(self, arg):
        error_args = {"password_forgot_error": "true"}
        next_page = self.contest_url()
        error_page = self.contest_url("passwordForgotten", **error_args)

        username = self.get_argument("username", "")

        try:
            #generate the new password.
            new_password = ''.join(random.choice(string.ascii_letters) for i in range(8))
            user_cur = self.sql_session.query(User).filter(User.username == username).first()
            user_cur.password = hash_password(new_password, "bcrypt")
            self.sql_session.commit()

            #now sending new password in plaintext to user
            sendMailNoAuth(user_cur.email, "Password Reset for Grader", f"Your password on the grader has been reset to: {new_password}\n If you have any questions please contact your Contest Administrator")



        except Exception as err:
            logger.warning(err)
            self.redirect(error_page)
            return

        logger.info("Password has been reset for user: " + user_cur.username)
        self.redirect(next_page)
