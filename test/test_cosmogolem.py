""" Tests for some of the static methods """

import time
from datetime import datetime
from CosmoGolem.bedtime import Bedtime
from CosmoGolem._helpers import WEEKDAYS


def test_weekend():
    """ Test that weekends are calculated correctly """
    for index, _ in enumerate(WEEKDAYS):
        day_to_check = datetime(2012, 1, 4 + index, 0)  # T'was a Monday
        is_weekend = Bedtime.check_if_next_morning_is_weekend(8, day_to_check)
        assert is_weekend == (True if day_to_check.weekday() >= WEEKDAYS.index("Saturday") else False), WEEKDAYS[
            day_to_check.weekday()
        ]

        day_to_check = datetime(2012, 1, 4 + index, 22)  # Check for tomorrow
        is_weekend = Bedtime.check_if_next_morning_is_weekend(8, day_to_check)
        assert is_weekend == (True if (day_to_check.weekday() + 1) >= WEEKDAYS.index("Saturday") else False), WEEKDAYS[
            day_to_check.weekday()
        ]
