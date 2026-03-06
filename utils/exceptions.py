"""
Custom exceptions used in Dino Park system
"""


class BookingAlreadyCancelledException(Exception):
    """
    Raised when trying to cancel a booking that is already cancelled
    """

    def __init__(self, message="Booking has already been cancelled"):
        super().__init__(message)