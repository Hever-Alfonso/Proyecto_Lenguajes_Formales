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

# --- STEP 5: LL(1) Stuff ---
def check_ll1(grammar, first, follow):
    """
    Check pairwise that FIRST(prodi) disjoint from FIRST(prodj),
    and if epsilon in FIRST, its FIRST intersect FOLLOW is empty.
    """
    for A, prods in grammar.items():
        for i in range(len(prods)):
            f_i = first_of_string(prods[i], first)
            for j in range(i+1, len(prods)):
                f_j = first_of_string(prods[j], first)
                if f_i & f_j:
                    return False
            if 'e' in f_i and (f_i & follow[A]):
                return False
    return True


def build_ll1_table(grammar, first, follow):
    """
    Build table[A][a] = which production to use when seeing a.
    """
    table = {A: {} for A in grammar}
    for A, prods in grammar.items():
        for prod in prods:
            fp = first_of_string(prod, first)
            for a in (fp - {'e'}):
                table[A][a] = prod
            if 'e' in fp:
                for b in follow[A]:
                    table[A][b] = prod
    return table

# --- STEP 6: LL(1) Predictive Parser ---
def predictive_parse(table, s, start):
    """
    Simulate LL(1) parse: push start, compare stack vs input,
    apply productions from table, return True/False.
    """
    stack = [start, '$']
    inp = list(s) + ['$']
    ip = 0
    while stack:
        top = stack.pop(0)
        cur = inp[ip]
        if top == cur == '$':
            return True
        if top == cur:
            ip += 1
        elif top in table and cur in table[top]:
            prod = table[top][cur]
            if prod != ['e']:
                for sym in reversed(prod):
                    stack.insert(0, sym)
        else:
            return False
    return False

# --- STEP 7: SLR(1) closure & states ---
def calculate_closure(items, grammar):
    """
    Given a set of LR(0) items, add new ones for nonterminals
    after the dot until no more appear. Return closure.
    """
    closure = set(items)
    changed = True
    while changed:
        changed = False
        new = set(closure)
        for (A, prod, i) in closure:
            if i < len(prod) and prod[i] in grammar:
                for beta in grammar[prod[i]]:
                    item = (prod[i], tuple(beta), 0)
                    if item not in new:
                        new.add(item)
                        changed = True
        closure = new
    return closure


def calculate_canonical_lr0(grammar, start):
    """
    Build the list of all LR(0) states and transitions between them.
    """
    init = (start, tuple(grammar[start][0]), 0)
    states = [calculate_closure({init}, grammar)]
    trans = {}
    idx_map = {tuple(states[0]): 0}
    changed = True
    while changed:
        changed = False
        for i, I in enumerate(list(states)):
            symbols = {prod[pos] for (A, prod, pos) in I if pos < len(prod)}
            for X in symbols:
                moved = {(A, prod, pos+1) for (A, prod, pos) in I if pos < len(prod) and prod[pos] == X}
                J = calculate_closure(moved, grammar)
                tJ = tuple(J)
                if tJ not in idx_map:
                    idx_map[tJ] = len(states)
                    states.append(J)
                    changed = True
                trans[(i, X)] = idx_map[tJ]
    return states, trans

# --- STEP 8: Construct SLR(1) table ---
def construct_slr_table(states, trans, grammar, follow, start):
    """
    Build ACTION/GO TO table: shift, reduce, accept.
    Returns table and production list for reduce mapping.
    """
    prods = []
    pidx = {}
    cnt = 0
    for A, alts in grammar.items():
        for beta in alts:
            prods.append((A, tuple(beta)))
            pidx[(A, tuple(beta))] = cnt
            cnt += 1
    table = [{} for _ in states]
    for i, I in enumerate(states):
        for (A, prod, pos) in I:
            if pos < len(prod):
                a = prod[pos]
                if (i, a) in trans:
                    table[i][a] = ('shift', trans[(i, a)])
            else:
                if A == start:
                    table[i]['$'] = ('accept',)
                else:
                    ridx = pidx[(A, prod)]
                    for a in follow[A]:
                        table[i][a] = ('reduce', ridx)
    return table, prods

# --- STEP 9: SLR(1) Parser simulation ---
def lr_parse(s, slr_table, productions):
    """
    Simulate SLR(1): use stack of states, read input, shift/reduce.
    Return True if accept state reached.
    """
    stack = [0]
    inp = list(s) + ['$']
    ip = 0
    while True:
        state = stack[-1]
        a = inp[ip]
        if a in slr_table[state]:
            act = slr_table[state][a]
            if act[0] == 'shift':
                stack.append(act[1]); ip += 1
            elif act[0] == 'reduce':
                A, beta = productions[act[1]]
                for _ in beta: stack.pop()
                t = stack[-1]
                stack.append(slr_table[t][A][1])
            elif act[0] == 'accept':
                return True
        else:
            return False
        
# --- MAIN: put it all together ---
def main():
    # 1) Read grammar and remember original nonterminals
    raw = read_grammar()
    original_NTs = list(raw.keys())
    grammar = convert_to_productions(raw)

    # 2) Quick productivity check (optional, omitted here)
    def productive_nts(grammar):
        productive = set()
        # Base: any NT that has a production of only terminals or 'e'
        for A, alts in grammar.items():
            for prod in alts:
                if all(sym not in grammar or sym == 'e' for sym in prod):
                    productive.add(A)
                    break
        # Iterate until no more NTs can be added
        changed = True
        while changed:
            changed = False
            for A, alts in grammar.items():
                if A in productive:
                    continue
                for prod in alts:
                    if all((sym not in grammar) or (sym in productive) for sym in prod):
                        productive.add(A)
                        changed = True
                        break
        return productive

    start = next(iter(grammar))
    if start not in productive_nts(grammar):
        print("Grammar is neither LL(1) nor SLR(1).")
        return

    # 3) Augment grammar and compute FIRST/FOLLOW
    aug = start + "'"
    grammar = {aug: [[start]], **grammar}
    first = calculate_first_sets(grammar)
    follow = calculate_follow_sets(grammar, first, aug)

    # 4) Determine which parser(s) apply
    is_ll1 = check_ll1(grammar, first, follow)
    if is_ll1:
        ll1_table = build_ll1_table(grammar, first, follow)

    states, trans = calculate_canonical_lr0(grammar, aug)
    slr_res = construct_slr_table(states, trans, grammar, follow, aug)
    is_slr1 = slr_res is not None
    if is_slr1:
        slr_table, slr_prods = slr_res

    # 5) Dispatch to the correct parsing mode
    # Case: neither LL(1) nor SLR(1)
    if not is_ll1 and not is_slr1:
        print("Grammar is neither LL(1) nor SLR(1).")
        return

    # Case: only LL(1)
    if is_ll1 and not is_slr1:
        print("Grammar is LL(1).")
        tests = []
        while True:
            s = input().strip()
            if not s:
                break
            tests.append(s)
        for s in tests:
            print("yes" if predictive_parse(ll1_table, s, aug) else "no")
        return

    # Case: only SLR(1)
    if is_slr1 and not is_ll1:
        print("Grammar is SLR(1).")
        tests = []
        while True:
            s = input().strip()
            if not s:
                break
            tests.append(s)
        for s in tests:
            print("yes" if lr_parse(s, slr_table, slr_prods) else "no")
        return

    # Case: both LL(1) and SLR(1) available
    while True:
        print("Select a parser (T: for LL(1), B: for SLR(1), Q: quit):")
        choice = input().strip().upper()
        if choice == 'Q':
            break
        if choice == 'T':
            tests = []
            while True:
                s = input().strip()
                if not s:
                    break
                tests.append(s)
            for s in tests:
                print("yes" if predictive_parse(ll1_table, s, aug) else "no")
        elif choice == 'B':
            tests = []
            while True:
                s = input().strip()
                if not s:
                    break
                tests.append(s)
            for s in tests:
                print("yes" if lr_parse(s, slr_table, slr_prods) else "no")
        else:
            print("Invalid choice, try T, B, or Q.")

if __name__ == '__main__':
    main()