def validate(value):
    # Note: Using isinstance(value, int) doesn't work here because bool is a
    # subclass of int.
    return (type(value) is int  # pylint: disable=unidiomatic-typecheck
            and 1 <= value <= 30)
