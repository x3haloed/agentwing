def merge(windows):
    windows.sort()
    result = []
    for start, end in windows:
        if result and start < result[-1][1]:
            result[-1] = (result[-1][0], end)
        else:
            result.append((start, end))
    return result
