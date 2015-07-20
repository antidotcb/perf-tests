__author__ = 'Danylo Bilyk'


class JsonMessage(object):
    def __init__(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, dict):
                self.__set_values(arg)
            elif isinstance(arg, object):
                self.__set_values(arg.__dict__)
            else:
                raise TypeError('Unnamed arguments are accepted only in form dictionaries or objects.')
        # priority is given to directly passed named arguments, their value override copied values
        self.__set_values(kwargs)

    def __set_values(self, values):
        if not isinstance(values, dict):
            raise TypeError('Values to setup should be a dictionary.')
        for attr, value in values.iteritems():
            if str(attr).startswith('_'):
                continue  # skip `private` members, only public variables are copied
            if str(attr) in self.__dict__.keys():
                # setup only object existing values
                setattr(self, attr, value)

    def __str__(self):
        return str(self.__dict__)
