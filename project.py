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

# --- STEP 3: Compute FIRST sets ---
def first_of_string(alpha, first):
    """
    Given a list of symbols alpha and precomputed first{},
    compute FIRST(alpha) = terminals that can start alpha, or 'e'.
    """
    result = set()
    for X in alpha:
        # if X is terminal (not in first), just return that
        if X not in first:
            result.add(X)
            return result
        # else X is NT: add FIRST(X) minus epsilon
        result |= (first[X] - {'e'})
        if 'e' not in first[X]:
            return result
    # all symbols can vanish -> epsilon
    result.add('e')
    return result


def calculate_first_sets(grammar):
    """
    Iteratively fill first[NT] for every nonterminal NT
    until no changes happen. Handles epsilon.
    """
    first = {A: set() for A in grammar}
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            for prod in prods:
                if prod == ['e']:
                    # NT -> epsilon
                    if 'e' not in first[A]:
                        first[A].add('e')
                        changed = True
                else:
                    temp = first_of_string(prod, first)
                    if not temp.issubset(first[A]):
                        first[A] |= temp
                        changed = True
    return first

# --- STEP 4: Compute FOLLOW sets ---
def calculate_follow_sets(grammar, first, start):
    """
    Compute follow[NT] = terminals that can come after NT.
    start gets '$'. Uses first{} and follow{} iteratively.
    """
    follow = {A: set() for A in grammar}
    follow[start].add('$')
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            for prod in prods:
                for i, B in enumerate(prod):
                    if B in grammar:  # B is a nonterminal
                        beta = prod[i+1:]
                        before = len(follow[B])
                        if beta:
                            fb = first_of_string(beta, first)
                            follow[B] |= (fb - {'e'})
                            if 'e' in fb:
                                follow[B] |= follow[A]
                        else:
                            follow[B] |= follow[A]
                        if len(follow[B]) > before:
                            changed = True
    return follow