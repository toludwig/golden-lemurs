import numpy as np
import calendar as cal
import datetime

def commit_time_profile(commit_times,
                        binsize='1h',
                        period='week',
                        normed=True):
    '''
    From a list of commit times, make a histogram list with
    bins of size [1h | 2h | 3h | 4h | 6h | 12h | 1d | 2d | 3d]
    with respect to a period of one [week | month].
    Thus you get an activity profile of the period averaged over all times.
    If normed, the number of commits ber bin will be percentages.
    '''

    times = [datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ") for time in commit_times]

    days_per_period = 7 if period == 'week' else 31

    day_hour_matrix = np.zeros((days_per_period, 24))

    for time in times:
        if period == 'week':
            # get weekday
            month_day = time.day
            month     = time.month
            year      = time.year
            day = cal.weekday(year, month, month_day)
        elif period == 'month':
            day = time.day-1 # days start at 1, but matrix at 0

        hour = time.hour
        # incrementing a cell in the matrix
        day_hour_matrix[day][hour] += 1


    # summing over hours and/or days respectively
    bins = []
    if binsize[1] == 'h':
        hour_steps = int(binsize[0])
        # make a bin from hour_steps hours in succession
        for day in range(len(day_hour_matrix)):
            for i in range(0, 6, hour_steps):
                hours_in_bin = day_hour_matrix[day, i:i+hours_steps]
                bins += [np.sum(hours_in_bin)]
    elif binsize[1] == 'd':
        day_steps = int(binsize[0])
        # sum over all hours
        day_matrix = np.sum(day_hour_matrix, axis=1)
        # make a bin from day_steps days in succession
        for i in range(0, len(day_matrix), hour_steps):
            days_in_bin = day_matrix[i:i+hour_steps]
            bins += [np.sum(days_in_bin)]

    return bins
