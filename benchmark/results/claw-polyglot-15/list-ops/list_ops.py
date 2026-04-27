def append(list1, list2):
    """Append all items from list2 to the end of list1."""
    result = list1[:]
    for item in list2:
        result.append(item)
    return result


def concat(lists):
    """Concatenate all lists into one flattened list."""
    result = []
    for lst in lists:
        for item in lst:
            result.append(item)
    return result


def filter(function, list):
    """Return list of items for which function(item) is True."""
    result = []
    for item in list:
        if function(item):
            result.append(item)
    return result


def length(list):
    """Return the total number of items in the list."""
    count = 0
    for item in list:
        count += 1
    return count


def map(function, list):
    """Return list of results of applying function to each item."""
    result = []
    for item in list:
        result.append(function(item))
    return result


def foldl(function, list, initial):
    """Fold (reduce) each item into the accumulator from the left."""
    accumulator = initial
    for item in list:
        accumulator = function(accumulator, item)
    return accumulator


def foldr(function, list, initial):
    """Fold (reduce) each item into the accumulator from the right."""
    accumulator = initial
    # Process list in reverse order
    for item in reversed(list):
        accumulator = function(item, accumulator)
    return accumulator


def reverse(list):
    """Return list with all items in reversed order."""
    result = []
    for item in reversed(list):
        result.append(item)
    return result
