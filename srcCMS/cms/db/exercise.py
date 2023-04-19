"""
Class representing a exercise Object in the database
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.builtins.disabled import *  # noqa
from future.builtins import *  # noqa

from datetime import timedelta

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.schema import Column, ForeignKey, CheckConstraint, \
    UniqueConstraint
from sqlalchemy.types import Boolean, Integer, String, Unicode, DateTime, \
    Interval
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.dialects.postgresql import ARRAY, CIDR

from cmscommon.crypto import generate_random_password, build_password

from . import CastingArray, Codename, Base, Admin, Contest

class Exercise(Base):
    """
    Class to store a exercise.
    """

    __tablename__ = 'exercise'
    __table_args__ = (
        UniqueConstraint('contest_id', 'num'),
        UniqueConstraint('contest_id', 'name'),
    )

    # Auto incremented Primary key
    id = Column(
        Integer,
        primary_key=True,
        autoincrement='ignore_fk'
    )

    # Used for sorting
    num = Column(
        Integer,
        nullable=True)

    # Creating the relation to the Contest with backpopulation
    contest_id = Column(
        Integer,
        ForeignKey(Contest.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    contest = relationship(
        Contest,
        back_populates="exercises")

    # name of the exercise
    name = Column(
        Codename,
        nullable=False,
        unique=True
    )

    # Title of the exercise
    title = Column(
        Unicode,
        nullable=False,
    )

    # Tags of the exercise for filtering
    exercise_tags = Column(
        Unicode,
        nullable=True
    )

    tasks = relationship(
        "Task",
        collection_class=ordering_list("num"),
        order_by="[Task.num]",
        cascade="all",
        passive_deletes=True,
        back_populates="exercise"
    )

    def get_best_user_scores_sum(self, user):
        sum = 0
        for task in self.tasks:
            sum += task.get_best_score_for_user(user)
        return sum

