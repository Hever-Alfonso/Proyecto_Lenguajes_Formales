import sys

# --- STEP 1: Read the grammar from input ---
def read_grammar():
    """
    We read how many productions the user wants, skip any blank lines,
    then read exactly that many lines of the form:
        Nonterminal -> alt1 alt2 ...
    and store them in a dict raw[NT] = [alt1, alt2, ...].
    """
    # Keep reading until we get a non-empty line for the count
    while True:
        line = input().strip()
        if line:
            break
    try:
        n = int(line)
    except:
        raise ValueError("First line must be an integer > 0.")
    raw = {}
    count = 0
    # Now read exactly n productions, ignoring blank lines
    while count < n:
        line = input().strip()
        if not line:
            continue
        parts = line.split()
        # Make sure format is: NT -> alt1 alt2 ...
        if len(parts) < 3 or parts[1] != '->':
            raise ValueError(f"Invalid production format: {' '.join(parts)}")
        nt = parts[0]
        alts = parts[2:]    # list of right-hand sides as strings
        raw.setdefault(nt, []).extend(alts)
        count += 1
    return raw

# --- STEP 2: Convert those string alternatives into lists of symbols ---
def convert_to_productions(raw):
    """
    Change raw grammar: for each NT and each alt-string,
    turn alt 'abc' into ['a','b','c'], and 'e' into ['e'] for epsilon.
    """
    grammar = {}
    for A, alts in raw.items():
        grammar[A] = []
        for alt in alts:
            if alt == 'e':
                grammar[A].append(['e'])
            else:
                grammar[A].append(list(alt))
    return grammar
