from datetime import datetime
import pytz

def is_dst():
    """Determine wether or not Daylight Savings Time (DST)
    is currently in effect"""

    x = datetime(datetime.now().year, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('US/Eastern'))
    y = datetime.now(pytz.timezone('US/Eastern'))

    # if DST is in effct, their offsets will be different
    return not (y.utcoffset() == x.utcoffset())

print(is_dst())