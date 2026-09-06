def merge(windows):
    intervals = []
    for start, end in windows:
        if start > end:
            raise ValueError("reversed interval")
        if start != end:
            intervals.append((start, end))
    result = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1]:
            result[-1] = (result[-1][0], max(result[-1][1], end))
        else:
            result.append((start, end))
    return result
