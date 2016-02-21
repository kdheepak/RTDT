def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def stop_time_update_to_dict(stu):

    return({
        'stop_sequence': stu.stop_sequence,
        'arrival': {
            'time': stu.arrival.time,
            'uncertainty': stu.arrival.uncertainty,
            'delay': stu.arrival.delay
        },
        'departure': {
            'time': stu.departure.time,
            'uncertainty': stu.departure.uncertainty,
            'delay': stu.departure.delay
        },
        'schedule_relationship': 'SCHEDULED' if stu.schedule_relationship==0 else 'UNKNOWN'
    })
