"""
Random number service class.
"""

from random import random

from api.entrypoints.v1.random_number.schema import RandomResponse


class RandomNumberService:
    """
    Random number service class.
    """

    @staticmethod
    async def get_random_number() -> RandomResponse:
        """
        Get random number.

        :returns: random number.
        """
        random_value = round(random() * 100, 2)
        return RandomResponse(message=random_value)
