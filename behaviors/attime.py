import datetime

import behavior


type_dict = {'attime': AtTime}

class AtTime(behavior.Behavior):
    def __init__(self, behavior, trigger_time):
        if datetime.datetime.now() > trigger_time:
            # If the trigger time has passed for today, just trigger it tomorrow at that time.
            trigger_time += datetime.timedelta(days=1)
        self._trigger_time = trigger_time
        self._behavior = behavior
        self._triggered = False

    def __call__(self):
        if datetime.datetime.now() >= self._trigger_time:
            self._triggered = True
            return self._behavior

    def cleanup(self):
        pass

    def stop(self):
        return self._triggered

    @classmethod
    def config(cls, conf_dict):
        param_missing = '%s parameter missing from configuration'

        if 'time' not in conf_dict:
            raise KeyError(param_missing % 'time')
        else:
            time = conf_dict['time']
            try:
                time_obj = datetime.datetime.strptime(time, '%H%M').time()
            except Exception:
                raise ValueError('Given time value %s is invalid. It should be in 24-hour HHMM format' % time)

        if 'seconds' in conf_dict:
            try:
                seconds = float(conf_dict['seconds'])
                # It makes no sense for this value to be 0.
                assert 0 < seconds and seconds < 60
            except Exception:
                raise ValueError('Given seconds value %s is invalid. It must be between 0 and 60.' % seconds)
            else:
                seconds_obj = datetime.timedelta(seconds=seconds)
                time_obj += seconds_obj

        if 'date' in conf_dict:
            date = conf_dict['date']
            try:
                date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            except Exception:
                raise ValueError('Given date value %s is invalid. It must be in the format YYYY-MM-DD.' % date)
        else:
            date_obj = datetime.datetime.today().date()

        if 'behavior' not in conf_dict:
            raise KeyError(param_missing % 'behavior')
        else:
            behavior = conf_dict['behavior']

        return cls(behavior, datetime.datetime.combine(date_obj, time_obj))
