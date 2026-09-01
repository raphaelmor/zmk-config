#!/usr/bin/env python3
"""Check a preprocessed TOTEM keymap for structural errors.

Run via scripts/check-keymap.sh, which does the preprocessing first.

Checks:
  1. every keymap layer binds exactly 38 keys
  2. the layers appear in the expected order, since node order is layer index
  3. combo key positions exist, are unique, and no combo shadows another
  4. both alpha bases put the expected letter on the expected position
  5. every behavior invocation supplies exactly as many parameters as that
     behavior's #binding-cells declares

Check 4 is the one that earns its keep: it compares the built keymap against the
letter-to-position mapping taken from the QMK userspace, which stays the spec
source of truth (users/raphaelmor/layers/{HDP,CMK}-defs.h).

Check 5 catches the class of bug where a 0-cell behavior is handed a parameter
that devicetree then silently drops, or where a multi-token macro like BT_CLR
(which expands to "BT_CLR_CMD 0") is miscounted.
"""
import re
import sys

TOTEM_KEYS = 38

# Layer order must match the l_* defines in config/ramo/ramo_config.dtsi, which
# match the enum in the QMK userspace (users/raphaelmor/ramo_layers.h).
EXPECT_LAYER_ORDER = [
    "layer_cmk", "layer_hdp", "layer_med", "layer_nav",
    "layer_mos", "layer_sym", "layer_num", "layer_fun",
]

# 18 combos ported from ramo_combos.c, plus the base-recovery chord.
EXPECT_COMBOS = 19

# Position name -> index, from config/keynames_totem.h.
NAMES = {}
for _i, _n in enumerate("LT4 LT3 LT2 LT1 LT0 RT0 RT1 RT2 RT3 RT4".split()):
    NAMES[_n] = _i
for _i, _n in enumerate("LM4 LM3 LM2 LM1 LM0 RM0 RM1 RM2 RM3 RM4".split(), 10):
    NAMES[_n] = _i
for _i, _n in enumerate(
        "LB5 LB4 LB3 LB2 LB1 LB0 RB0 RB1 RB2 RB3 RB4 RB5".split(), 20):
    NAMES[_n] = _i
for _i, _n in enumerate("LH2 LH1 LH0 RH0 RH1 RH2".split(), 32):
    NAMES[_n] = _i
INDEX = {v: k for k, v in NAMES.items()}

# Expected alphas, transcribed from the QMK layer defs.
EXPECT_ALPHAS = {
    "layer_hdp": {      # users/raphaelmor/layers/HDP-defs.h
        "LT4": "V", "LT3": "W", "LT2": "G", "LT1": "M", "LT0": "J",
        "LM4": "S", "LM3": "N", "LM2": "T", "LM1": "H", "LM0": "K",
        "LB4": "F", "LB3": "P", "LB2": "D", "LB1": "L", "LB0": "X",
        "RM1": "A", "RM2": "E", "RM3": "I", "RM4": "C",
        "RB1": "U", "RB2": "O", "RB3": "Y", "RB4": "B",
    },
    "layer_cmk": {      # users/raphaelmor/layers/CMK-defs.h
        "LT4": "Q", "LT3": "W", "LT2": "F", "LT1": "P", "LT0": "G",
        "LM4": "A", "LM3": "R", "LM2": "S", "LM1": "T", "LM0": "D",
        "LB4": "Z", "LB3": "X", "LB2": "C", "LB1": "V", "LB0": "B",
        "RT0": "J", "RT1": "L", "RT2": "U", "RT3": "Y",
        "RM0": "H", "RM1": "N", "RM2": "E", "RM3": "I", "RM4": "O",
        "RB0": "K", "RB1": "M",
    },
}

# Only real keymap layers carry display-name; behavior nodes do not.
LAYER_RE = re.compile(
    r"(\w+)\s*\{\s*display-name\s*=\s*\"([^\"]*)\"\s*;\s*"
    r"bindings\s*=\s*<(.*?)>\s*;", re.S)

COMBO_RE = re.compile(
    r"(combo_\w+)\s*\{\s*bindings\s*=\s*<(.*?)>\s*;\s*"
    r"key-positions\s*=\s*<(.*?)>\s*;\s*layers\s*=\s*<(.*?)>\s*;", re.S)

# HID keyboard page 0x07, A=0x04 .. Z=0x1D.
USAGE_RE = re.compile(r"\(0x07\) << 16\) \| \(0x([0-9A-Fa-f]+)\)")

# A labelled leaf node declaring #binding-cells. Leaf, so no nested braces.
CELLS_RE = re.compile(
    r"(\w+)\s*:\s*\w+\s*\{[^{}]*?#binding-cells\s*=\s*<(\d+)>", re.S)

# Any bindings property, plus the node body preceding it, so the owner can be
# identified. Behavior nodes deliberately leave parameters off their child
# bindings (the parent injects them), so only keymap layers, combos and macros
# are arity-checked.
BINDINGS_RE = re.compile(r"bindings\s*=\s*([^;]*);", re.S)


def tokenize(group):
    """Split a bindings value into behavior refs and parameter tokens.

    A parenthesised expression counts as a single parameter no matter how much
    whitespace it contains, which is what makes preprocessed keycodes work:
    they arrive as things like ((((0x07) << 16) | (0x0B))).

    "<" and ">" are treated as separators rather than parsed, because a cell list
    delimiter and the left-shift inside a keycode expression look identical to a
    regex. Shifts only ever appear inside parentheses, which are consumed whole,
    so the delimiters are the only "<" left at depth zero.
    """
    out, i, n = [], 0, len(group)
    while i < n:
        c = group[i]
        if c.isspace() or c in ",<>":
            i += 1
        elif c == "&":
            j = i + 1
            while j < n and (group[j].isalnum() or group[j] == "_"):
                j += 1
            out.append(("beh", group[i:j]))
            i = j
        elif c == "(":
            depth, j = 0, i
            while j < n:
                if group[j] == "(":
                    depth += 1
                elif group[j] == ")":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
            out.append(("param", group[i:j]))
            i = j
        else:
            j = i
            while j < n and not group[j].isspace() and group[j] not in "(),<>":
                j += 1
            if j == i:
                i += 1
            else:
                out.append(("param", group[i:j]))
                i = j
    return out


def check_arity(group, cells, where, problems):
    """Walk a cell list the way devicetree does: each ref consumes its cells."""
    toks = tokenize(group)
    i = 0
    while i < len(toks):
        kind, val = toks[i]
        if kind != "beh":
            problems.append("%s: stray parameter %r with no behavior" % (where, val))
            i += 1
            continue
        label = val[1:]
        if label not in cells:
            problems.append("%s: unknown behavior %s" % (where, val))
            i += 1
            continue
        want = cells[label]
        got, j = 0, i + 1
        while j < len(toks) and toks[j][0] == "param" and got < want:
            got += 1
            j += 1
        if got != want:
            problems.append("%s: %s wants %d parameter(s), got %d"
                            % (where, val, want, got))
        i = j


def bindings_of(body):
    """Split a bindings block into individual bindings (each starts with &)."""
    return [p.strip() for p in re.split(r"(?=&\w+)", body) if p.strip().startswith("&")]


def letter_at(body, index):
    """Decode binding `index` to a letter, whether plain &kp or a mod-tap's tap."""
    parts = bindings_of(body)
    if index >= len(parts):
        return "<missing>"
    hits = USAGE_RE.findall(parts[index])
    if hits:
        code = int(hits[-1], 16)
        if 0x04 <= code <= 0x1D:
            return chr(ord("A") + code - 0x04)
        return "0x%02X" % code
    return parts[index].split()[0]


def main(path):
    src = open(path).read()
    ok = True

    layers = LAYER_RE.findall(src)
    by_node = {node: body for node, _disp, body in layers}

    print("=== LAYERS (expect %d bindings each) ===" % TOTEM_KEYS)
    for i, (node, disp, body) in enumerate(layers):
        n = len(bindings_of(body))
        good = n == TOTEM_KEYS
        ok &= good
        print("  [%d] %s %-12s %-9s %3d bindings"
              % (i, "ok " if good else "BAD", node, disp, n))

    order = [node for node, _d, _b in layers]
    if order != EXPECT_LAYER_ORDER:
        ok = False
        print("\n  !! layer order is wrong -- node order IS the layer index")
        print("     want: %s" % " ".join(EXPECT_LAYER_ORDER))
        print("     got:  %s" % " ".join(order))
    else:
        print("\n  ok  %d layers, in the expected order" % len(layers))

    for node, expect in EXPECT_ALPHAS.items():
        print("\n=== ALPHAS: %s ===" % node)
        body = by_node.get(node)
        if body is None:
            ok = False
            print("  !! layer not found")
            continue
        bad = []
        for name, want in sorted(expect.items(), key=lambda kv: NAMES[kv[0]]):
            got = letter_at(body, NAMES[name])
            if got != want:
                bad.append("%s (position %d): want %s, got %s"
                           % (name, NAMES[name], want, got))
        if bad:
            ok = False
            for b in bad:
                print("  !! %s" % b)
        else:
            print("  ok  all %d letters on their expected positions" % len(expect))

    print("\n=== COMBOS ===")
    combos = COMBO_RE.findall(src)
    items, seen = [], {}
    for name, _binding, pos, layers_prop in combos:
        positions = [int(p) for p in pos.split()]
        note = ""
        out_of_range = [p for p in positions if not 0 <= p < TOTEM_KEYS]
        if out_of_range:
            ok = False
            note += "  !! position out of range: %s" % out_of_range
        key = (tuple(sorted(positions)), layers_prop.strip())
        if key in seen:
            ok = False
            note += "  !! same keys and layers as %s" % seen[key]
        seen[key] = name
        items.append((name, set(positions), layers_prop.strip()))
        labels = "+".join(INDEX.get(p, str(p)) for p in positions)
        print("  %-14s %-16s layers=[%s]%s"
              % (name, labels, layers_prop.strip(), note))

    if len(combos) != EXPECT_COMBOS:
        ok = False
        print("\n  !! combo count %d, expected %d" % (len(combos), EXPECT_COMBOS))
    else:
        print("\n  ok  %d combos" % len(combos))

    # A combo whose keys are a subset of another's, sharing a layer, always wins —
    # the superset can then never fire.
    shadowed = False
    for na, sa, la in items:
        for nb, sb, lb in items:
            if na != nb and sa < sb and (set(la.split()) & set(lb.split())):
                ok = shadowed = False
                print("  !! %s %s shadows %s %s"
                      % (na, sorted(sa), nb, sorted(sb)))
    if not shadowed:
        print("  ok  no combo shadows another")

    # ---- parameter arity ----------------------------------------------------
    print("\n=== PARAMETER ARITY ===")
    cells = {label: int(n) for label, n in CELLS_RE.findall(src)}
    print("  %d behaviors declare #binding-cells" % len(cells))

    problems = []

    # keymap layers
    for node, _disp, body in layers:
        check_arity(body, cells, node, problems)

    # combos
    for name, binding, _pos, _lp in combos:
        check_arity(binding, cells, name, problems)

    # macros: parameters here are real, unlike a hold-tap's child bindings
    for mnode in re.finditer(
            r"(\w+)\s*:\s*\w+\s*\{([^{}]*?compatible\s*=\s*"
            r"\"zmk,behavior-macro\"[^{}]*?)\}", src, re.S):
        label, body = mnode.group(1), mnode.group(2)
        m = BINDINGS_RE.search(body)
        if m:
            check_arity(m.group(1), cells, "macro %s" % label, problems)

    if problems:
        ok = False
        for p in problems:
            print("  !! %s" % p)
    else:
        print("  ok  every behavior invocation supplies the right parameter count")

    print("\n=== %s ===" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/totem.pre"))
