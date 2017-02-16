from rest_framework import throttling


class BurstRateThrottle(throttling.UserRateThrottle):
    """
    Facilitates applying a burst throttle rate in addition to a longer
    term sustained throttle rate.
    """
    scope = 'burst'


class SustainedRateThrottle(throttling.UserRateThrottle):
    """
    Facilitates applying a sustained throttle rate in addition to a
    shorter term burst throttle rate.
    """
    scope = 'sustained'
