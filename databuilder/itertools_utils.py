import itertools


def eager_iterator(iterator):
    """
    Transparently wraps an iterator, but eagerly consumes the first item so as to
    execute any generator set up code and trigger any errors which might occur
    """
    try:
        first_item = next(iterator)
    except StopIteration:
        # If the original iterator was empty there's nothing more to do
        return iterator
    # Otherwise chain the first item back on to the front and continue
    return itertools.chain([first_item], iterator)
