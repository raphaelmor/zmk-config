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
  6. the adaptive-key rule set matches the QMK source it was ported from

Check 4 is the one that earns its keep: it compares the built keymap against the
letter-to-position mapping taken from the QMK userspace, which stays the spec
source of truth (users/raphaelmor/layers/{HDP,CMK}-defs.h). It follows letters
through the adaptive layer, so &ak_V resolves via that behavior's default binding.

Check 5 catches the class of bug where a 0-cell behavior is handed a parameter that
devicetree then silently drops, or where a multi-token macro like BT_CLR (which
expands to "BT_CLR_CMD 0") is miscounted.

Check 6 guards the thing most likely to rot: 20 adaptive rules transcribed by hand
from ramo_adaptive.c, plus CommaMagic on every letter.
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

# The 20 two-key adaptive rules, transcribed from users/raphaelmor/ramo_adaptive.c.
# host letter -> {prior letter: output sequence}. The two 3-key rules there
# (P.B.D -> PWD, W.M.G -> WML) are deliberately absent: the module tracks one
# prior key.
EXPECT_RULES = {
    "D": {"P": "W D"},
    "F": {"P": "S"},
    "G": {"K": "L", "M": "BSPC L G", "J": "P G", "W": "D"},
    "H": {"K": "N"},
    "J": {"G": "T H", "W": "L"},
    "K": {"M": "BSPC L K", "H": "BSPC N K"},
    "M": {"G": "L", "V": "L"},
    "P": {"F": "BSPC S P"},
    "V": {"G": "T", "M": "BSPC L V"},
    "W": {"G": "D", "M": "P"},
    "B": {"Y": "BSPC I B"},
    "E": {"A": "U"},
}

# Letters that get CommaMagic. Q is excluded: it has no key on the Hands Down base,
# only the W+M combo, whose output goes through a macro rather than a keycode.
EXPECT_COMMAMAGIC = sorted(set("ABCDEFGHIJKLMNOPRSTUVWXYZ"))

LAYER_RE = re.compile(
    r"(\w+)\s*\{\s*display-name\s*=\s*\"([^\"]*)\"\s*;\s*"
    r"bindings\s*=\s*<(.*?)>\s*;", re.S)

COMBO_RE = re.compile(
    r"(combo_\w+)\s*\{\s*bindings\s*=\s*<(.*?)>\s*;\s*"
    r"key-positions\s*=\s*<(.*?)>\s*;\s*layers\s*=\s*<(.*?)>\s*;", re.S)

NODE_RE = re.compile(r"(\w+)\s*:\s*(\w+)\s*\{")
BINDINGS_RE = re.compile(r"bindings\s*=\s*([^;]*);", re.S)
CELLS_RE = re.compile(r"#binding-cells\s*=\s*<(\d+)>")

# HID keyboard page 0x07: A=0x04 .. Z=0x1D, and a few named keys we want to show.
USAGE_RE = re.compile(r"\(0x07\) << 16\) \| \(0x([0-9A-Fa-f]+)\)")
NAMED = {0x2A: "BSPC", 0x28: "RET", 0x2C: "SPACE", 0x2B: "TAB", 0x29: "ESC"}


def usage_name(code):
    if 0x04 <= code <= 0x1D:
        return chr(ord("A") + code - 0x04)
    return NAMED.get(code, "0x%02X" % code)


def scan_nodes(src):
    """Return {label: body} for every labelled node, by brace matching.

    Regex alone cannot do this: adaptive-key nodes contain child nodes, so any
    [^{}] body pattern stops at the first child.
    """
    out = {}
    for m in NODE_RE.finditer(src):
        label, start = m.group(1), m.end() - 1
        depth, i, n = 0, start, len(src)
        while i < n:
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out[label] = src[start + 1:i]
    return out


def tokenize(group):
    """Split a bindings value into behavior refs and parameter tokens.

    A parenthesised expression counts as a single parameter no matter how much
    whitespace it contains, which is what makes preprocessed keycodes work: they
    arrive as things like ((((0x07) << 16) | (0x0B))).

    "<" and ">" are separators rather than parsed, because a cell-list delimiter and
    the left-shift inside a keycode expression look identical to a regex. Shifts only
    appear inside parentheses, which are consumed whole, so the delimiters are the
    only "<" left at depth zero.
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


def bindings_of(body):
    return [t for t in tokenize(body) if t[0] == "beh"]


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


def seq_of(group):
    """Render a bindings value as a space-separated list of key names."""
    names = []
    for kind, val in tokenize(group):
        if kind == "param":
            hits = USAGE_RE.findall(val)
            if hits:
                names.append(usage_name(int(hits[-1], 16)))
    return " ".join(names)


def main(path):
    src = open(path).read()
    ok = True
    nodes = scan_nodes(src)
    cells = {label: int(CELLS_RE.search(body).group(1))
             for label, body in nodes.items() if CELLS_RE.search(body)}

    # adaptive default bindings, so &ak_V can be resolved back to a letter
    ak_letter = {}
    for label, body in nodes.items():
        if "zmk,behavior-adaptive-key" in body:
            m = BINDINGS_RE.search(body)
            if m:
                ak_letter[label] = seq_of(m.group(1))

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

    def letter_at(body, index):
        """Decode binding `index`: plain &kp, a mod-tap's tap, or an adaptive."""
        parts = [v for k, v in tokenize(body) if k == "beh"]
        # rebuild each binding with its params so params stay attached
        toks, groups, cur = tokenize(body), [], None
        for kind, val in toks:
            if kind == "beh":
                cur = [val]
                groups.append(cur)
            elif cur is not None:
                cur.append(val)
        if index >= len(groups):
            return "<missing>"
        grp = groups[index]
        label = grp[0][1:]
        if label in ak_letter:                      # &ak_V -> its default binding
            return ak_letter[label]
        hits = USAGE_RE.findall(" ".join(grp[1:]))  # &kp X or &mt_X MOD X
        if hits:
            return usage_name(int(hits[-1], 16))
        return grp[0]

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

    # ---- adaptive rules -----------------------------------------------------
    if ak_letter:
        print("\n=== ADAPTIVE RULES vs ramo_adaptive.c ===")
        missing_cap, rule_problems = [], []
        for letter in EXPECT_COMMAMAGIC:
            label = "ak_%s" % letter
            if label not in nodes:
                missing_cap.append(letter)
                continue
            body = nodes[label]
            if "cap {" not in body and "cap{" not in body:
                missing_cap.append(letter)
        if missing_cap:
            ok = False
            print("  !! no CommaMagic on: %s" % " ".join(missing_cap))
        else:
            print("  ok  CommaMagic on all %d letters (Q excluded by design)"
                  % len(EXPECT_COMMAMAGIC))

        total = 0
        for host, rules in sorted(EXPECT_RULES.items()):
            body = nodes.get("ak_%s" % host)
            if body is None:
                rule_problems.append("ak_%s missing entirely" % host)
                continue
            # every trigger child except the CommaMagic one
            found = {}
            for tm in re.finditer(
                    r"(\w+)\s*\{\s*trigger-keys\s*=\s*<(.*?)>\s*;.*?"
                    r"bindings\s*=\s*([^;]*);", body, re.S):
                name, trig, binds = tm.group(1), tm.group(2), tm.group(3)
                trig_names = [usage_name(int(h, 16))
                              for h in USAGE_RE.findall(trig)]
                if name == "cap":
                    continue
                for t in trig_names:
                    found[t] = seq_of(binds)
            for prior, want in sorted(rules.items()):
                total += 1
                got = found.get(prior)
                if got != want:
                    rule_problems.append(
                        "%s after %s: want %r, got %r" % (host, prior, want, got))
            extra = set(found) - set(rules)
            for e in sorted(extra):
                rule_problems.append(
                    "%s after %s: rule not in ramo_adaptive.c (%r)"
                    % (host, e, found[e]))
        if rule_problems:
            ok = False
            for p in rule_problems:
                print("  !! %s" % p)
        else:
            print("  ok  all %d two-key rules match, no extras" % total)

        # The module keeps one pressed_bindings slot per instance, so an adaptive
        # reachable from two places could be held twice. Counted on the
        # PREPROCESSED source, which has no comments to miscount.
        shared = []
        for label in sorted(ak_letter):
            refs = len(re.findall(r"&%s\b" % label, src))
            if refs > 1:
                shared.append("%s referenced %d times" % (label, refs))
        if shared:
            ok = False
            for s in shared:
                print("  !! %s -- one pressed_bindings slot per instance" % s)
        else:
            print("  ok  each of the %d adaptives is referenced exactly once"
                  % len(ak_letter))

    # ---- combos -------------------------------------------------------------
    print("\n=== COMBOS ===")
    combos = COMBO_RE.findall(src)
    items, seen = [], {}
    for name, binding, pos, layers_prop in combos:
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
    print("  %d behaviors declare #binding-cells" % len(cells))
    problems = []
    for node, _disp, body in layers:
        check_arity(body, cells, node, problems)
    for name, binding, _pos, _lp in combos:
        check_arity(binding, cells, name, problems)
    for label, body in nodes.items():
        # macros and adaptives supply real parameters; a hold-tap's child bindings
        # deliberately do not, because the parent injects them.
        if ("zmk,behavior-macro" in body
                or "zmk,behavior-adaptive-key" in body):
            for m in BINDINGS_RE.finditer(body):
                check_arity(m.group(1), cells, "%s" % label, problems)

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
