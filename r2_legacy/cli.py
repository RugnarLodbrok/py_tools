def ask_yes_no(message, key=None):
    """
    Ask user a question and expect one of (yes, no, always, never)

    :param message: message
    :param key: hashable key for remembering whe received always or never
    :return: Boolean answer
    """
    key = key or message
    if key in _yes_no_memory:
        return _yes_no_memory[key]

    answer = input('{} (yes/no): '.format(message)).lower()
    while True:
        if answer in ('yes', 'y'):
            return True
        if answer in ('no', 'n'):
            return False
        if answer == 'always':
            _yes_no_memory[key] = True
            return True
        if answer == 'never':
            _yes_no_memory[key] = False
            return False
        answer = input("`yes' or `no':\n")


_yes_no_memory = {}


def input_integer(message, validation_func=None, validation_message=None):
    i = input('{}:\n'.format(message))
    while True:
        try:
            ret = int(i)
        except ValueError:
            i = input('Integer is required: ')
        else:
            if validation_func is None or validation_func(ret):
                return ret
            i = input(validation_message or 'Invalid, try again:\n')
