from datetime import datetime, timedelta
import utility.time_utils as time_utils

def from_iso_format( iso_str ):
    return datetime.fromisoformat(iso_str)

def is_current_posting_time_within_window( earliest_scheduled_datetime_str ):
    '''
        Allow for a threshold of a minute in each direction of the scheduled time to allow and honest
        check of whether or not we are running this at the time of a scheduled post.

        Params:
            datetime scheduled_time:  the remotely stored value of when we have calculated our next posting should be
            datetime current_time: the time we have started the run of this app

        Returns:
            boolean: are we running this close enough to the scheduled date
    '''
    if (earliest_scheduled_datetime_str is None):
        print(f'🔥 NO earliest_scheduled_datetime_str')
        return False
    
    formatted_iso=time_utils.convert_str_to_iso_format(earliest_scheduled_datetime_str.strip())
    scheduled_time=datetime.fromisoformat(formatted_iso)
    current_time=datetime.now()
    
    lower_bound=scheduled_time - timedelta(minutes=10)
    upper_bound=scheduled_time + timedelta(minutes=10)

    if lower_bound < current_time < upper_bound:
        print(f'✅ CURRENT TIME : {current_time} is between posting window {lower_bound} and {upper_bound}')
        return True
    else:
        print(f'❌ CURRENT TIME : {current_time} is NOT between posting window {lower_bound} and {upper_bound}')
        return False

def convert_str_to_iso_format(date_str):
    """
    Converts a date string in the format '%Y-%m-%d %H:%M:%S' to the ISO format '%Y-%m-%dT%H:%M:%S'.

    Args:
        date_str (str): The input date string to be converted.

    Returns:
        str: The converted date string in ISO format, or None if an error occurs.
    """
    try:
        # First, parse the input string to create a datetime object
        date_obj=datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        # Then, format the datetime object to the desired ISO format
        iso_format_str=date_obj.strftime("%Y-%m-%dT%H:%M:%S")
        return iso_format_str

    except ValueError as e:
        # If the input string is not in the expected format, catch the ValueError exception
        # and return None
        return date_str

def is_expired( posting_datetime_str ):
    '''
        Checks to see if the current iso string is in the past

        @returns:
            True of False
    '''
    if (posting_datetime_str == ''):
        return False
    trimmed_datetime_now = datetime.now().replace(microsecond=0, second=0)
    is_posting_time_before_now = datetime.fromisoformat(posting_datetime_str) < trimmed_datetime_now
    
    if (is_posting_time_before_now):
        print(f'❌ POSTING TIME {datetime.fromisoformat(posting_datetime_str)} IS BEFORE {trimmed_datetime_now}')
        return True
    else:
        return False
