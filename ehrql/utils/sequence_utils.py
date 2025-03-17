def ordered_set(sequence):
    """
    Deduplicates a sequence, maintaining order
    """
    return list(dict.fromkeys(sequence))
