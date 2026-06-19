#!/usr/bin/env python3
"""
Independently verify Math items: for each item's `spec` block, confirm exactly one answer
option is correct and that it matches the claimed key. This makes the answer-correctness
verification rule objective instead of trusting the generator.

Parses the standard question-set markdown (see references/output-format.md).

Usage:
    python scripts/check_math.py path/to/question-set.md
    python scripts/check_math.py --spec '{"given":["3*x+5=20"],"ask":"x","options":{...},"correct":"B"}'

Exit code 0 if all auto-verifiable items pass; 1 otherwise.
Requires sympy:  pip install sympy --break-system-packages
"""
import argparse, json, re, sys

try:
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr
except ImportError:
    print("ERROR: sympy not installed. Run: pip install sympy --break-system-packages")
    sys.exit(2)

# The trailing ```` ``` ```` anchor forces the non-greedy body to the OUTER closing brace,
# so nested option objects parse correctly.
SPEC_RE = re.compile(r"```spec\s*(\{.*?\})\s*```", re.DOTALL)
ITEM_RE = re.compile(r"^##\s+Item\s+(\d+)\b", re.MULTILINE)


def _to_expr(s):
    """'a = b' -> 'a - (b)' so it can be solved; plain expressions pass through."""
    if "=" in s:
        lhs, rhs = s.split("=", 1)
        return parse_expr(f"({lhs}) - ({rhs})")
    return parse_expr(s)


def check_spec(spec):
    """Return (ok, message): True=pass, False=fail, None=unverifiable-by-script."""
    if spec.get("verify") == "manual":
        return None, "verify=manual — script cannot check; verify by hand"
    try:
        given = [_to_expr(g) for g in spec.get("given", [])]
        ask = spec["ask"]
        options = spec["options"]
        claimed = spec["correct"]

        symbols = sorted(set().union(*[e.free_symbols for e in given]) if given else set(),
                         key=lambda s: s.name)
        ask_sym = sp.Symbol(ask) if re.fullmatch(r"[A-Za-z_]\w*", ask) else None

        if given:
            sols = sp.solve(given, symbols, dict=True)
            if not sols:
                return False, "no solution to `given`; spec is inconsistent"
            sol = sols[0]
            true_val = sol.get(ask_sym) if (ask_sym is not None and ask_sym in sol) \
                else parse_expr(ask).subs(sol)
        else:
            true_val = parse_expr(ask)
        true_val = sp.simplify(true_val)

        matches = []
        for letter, val in options.items():
            try:
                if sp.simplify(parse_expr(str(val)) - true_val) == 0:
                    matches.append(letter)
            except Exception as e:
                return False, f"option {letter} unparseable: {e}"

        if len(matches) != 1:
            return False, f"expected exactly one correct option, found {matches or 'none'} (true value = {true_val})"
        if matches[0] != claimed:
            return False, f"claimed correct {claimed}, but the unique correct option is {matches[0]}"
        return True, f"{claimed} is the unique correct option (= {true_val})"
    except KeyError as e:
        return False, f"spec missing field: {e}"
    except Exception as e:
        return False, f"could not evaluate spec: {e}"


def iter_items(md):
    starts = [(m.group(1), m.start()) for m in ITEM_RE.finditer(md)]
    for i, (num, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(md)
        yield num, md[start:end]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="question-set markdown file")
    ap.add_argument("--spec", help="check a single inline JSON spec")
    args = ap.parse_args()

    if args.spec:
        ok, msg = check_spec(json.loads(args.spec))
        tag = "PASS" if ok else ("SKIP" if ok is None else "FAIL")
        print(f"{tag}: {msg}")
        sys.exit(0 if ok in (True, None) else 1)

    if not args.path:
        ap.error("provide a markdown path or --spec")

    md = open(args.path).read()
    any_fail = False
    found = 0
    for num, block in iter_items(md):
        m = SPEC_RE.search(block)
        if not m:
            continue
        found += 1
        try:
            spec = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            print(f"Item {num}: FAIL — spec is not valid JSON: {e}")
            any_fail = True
            continue
        ok, msg = check_spec(spec)
        tag = "PASS" if ok else ("SKIP" if ok is None else "FAIL")
        print(f"Item {num}: {tag} — {msg}")
        if ok is False:
            any_fail = True
    if found == 0:
        print("No math specs found in file.")
    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
