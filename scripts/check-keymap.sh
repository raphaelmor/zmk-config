#!/usr/bin/env bash
#
# check-keymap.sh — structural check of the keymap, without a Zephyr toolchain.
#
# WHY THIS EXISTS
#   The only real build is GitHub Actions, and a round trip there costs minutes.
#   Most mistakes in a devicetree keymap are structural — a layer with the wrong
#   number of bindings, a combo pointing at a position that does not exist, a
#   letter on the wrong key — and all of those are visible after nothing more than
#   the C preprocessor. This runs that preprocessor and checks the result.
#
#   It does NOT replace the CI build. It cannot see devicetree binding violations,
#   Kconfig problems, or flash overflow. It is the fast first gate.
#
# USAGE
#   scripts/check-keymap.sh
#
# REQUIREMENTS
#   A local ZMK source tree for the headers. The west workspace at .zmk/zmk is
#   used if present. Override with ZMK_APP=/path/to/zmk/app.
#
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
zmk_app="${ZMK_APP:-$here/.zmk/zmk/app}"

if [ ! -d "$zmk_app/dts" ]; then
    echo "error: no ZMK source at $zmk_app"
    echo "       clone it, or point ZMK_APP at an existing app/ directory."
    exit 2
fi

# Two Zephyr headers are reachable from ZMK's includes but live in the Zephyr tree,
# which the local west workspace filters out (.zmk/.west/config, project-filter).
# Only these constants are needed, so stub them rather than clone Zephyr.
stub="$(mktemp -d)"
trap 'rm -rf "$stub"' EXIT
mkdir -p "$stub/zephyr/dt-bindings/input"
cat > "$stub/zephyr/dt-bindings/input/input-event-codes.h" <<'EOF'
#pragma once
#define INPUT_REL_X      0x00
#define INPUT_REL_Y      0x01
#define INPUT_REL_HWHEEL 0x06
#define INPUT_REL_WHEEL  0x08
EOF
cat > "$stub/zephyr/dt-bindings/dt-util.h" <<'EOF'
#pragma once
#define BIT(n) (1 << (n))
EOF

pre="$stub/totem.pre"

# assembler-with-cpp is what Zephyr itself uses to preprocess devicetree: it stops
# cpp from treating "#binding-cells" as an unknown preprocessor directive.
if ! clang -E -P -x assembler-with-cpp -nostdinc \
        -I "$zmk_app/dts" \
        -I "$zmk_app/include" \
        -I "$stub" \
        -I "$here/config" \
        "$here/config/totem.keymap" > "$pre"; then
    echo "error: preprocessing failed"
    exit 1
fi

echo "preprocessed $(wc -l < "$pre" | tr -d ' ') lines"
exec python3 "$here/scripts/check_keymap.py" "$pre"
