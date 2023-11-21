
""" 
    Find the stem (longest common substring) from a string array (arr)
    The only modification is that the substring has to be in the edges of the strings and len(substring) > 5
"""
def findstem(arr):
    # Determine size of the array
    n = len(arr)
    # Take first word from array
    # as reference
    s = arr[0]
    l = len(s)
    res = ""
    imax = 0
    for i in range(2):
        for j in range(5, l + 1):
            # generating all possible substrings
            # of our reference string arr[0] i.e s
            stem = s[:j]
            k = 1
            for k in range(1, n):
                # Check if the generated stem is
                # common to all words
                if stem not in arr[k]:
                    break
            # If current substring is present in
            # all strings and its length is greater
            # than current result
            if (k + 1 == n and len(res) < len(stem)):
                res = stem
                imax = i
        s = s[::-1]
    return res[::-1] if imax else res

