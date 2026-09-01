/*
 * hdp-config.h — Hands Down Promethium alpha rows
 *
 * SPDX-License-Identifier: MIT
 *
 * Ported from users/raphaelmor/layers/HDP-defs.h. Row-macro style follows
 * moutis' layouts/hd/pm-config.h so the two are directly comparable.
 *
 * This is moutis' canonical PM arrangement, with the customisations recorded in
 * HDPM-parity.md:17-20 kept: GACS home-row mods, Hyper and Meh on fixed top
 * positions, and Option-A thumbs aligned to Colemak.
 *
 *     ╭─────────────────────────╮      ╭─────────────────────────╮
 *     │  V   W   G   M   J      │      │      #   .   /   "   '  │
 *     │  S   N   T   H   K      │      │      ,   A   E   I   C  │
 * ⇧ₛ  │  F   P   D   L   X      │      │      -   U   O   Y   B  │  ⟳
 *     ╰───────────╮ ESC SPC TAB │      │  R  BSP ENT ╭───────────╯
 *                 ╰─────────────╯      ╰─────────────╯
 *
 *   Home-row mods (GACS): pinky ⌃ · ring ⌥ · middle ⌘ · index ⇧
 *   Hyper on G and /  ·  Meh on M and .
 *   Off-map letters:  Q via the W+M combo  ·  Z via the N+H combo
 *
 * The two positions the Corne did not have:
 *   LB5 = sticky shift  ·  RB5 = key repeat
 *
 * &key_repeat is ZMK's built-in equivalent of QMK's QK_REP, which
 * QMK-feature-audit.md:158-176 recommends as a T1 addition — same problem domain
 * as the adaptive engine (killing same-finger bigrams) but with no collision risk,
 * because it never rewrites already-typed text.
 *
 * These are NOT the four "// TODO: should be a real key once a use is found"
 * positions from HDP-defs.h:33,35,49,51 — those are the ex2 keys, which the Totem
 * does not have and the port drops. LB5 and RB5 are genuinely new keys, and both
 * are free slots: change them without consequence.
 */

#pragma once

#define HDP_label "HD-Pm"

//                  LT4              LT3              LT2                LT1              LT0
#define HDP_LT      &kp V            &kp W            &hml HYPER G       &hml MEH M       &kp J
#define HDP_LM      &hml LCTRL S     &hml LALT N      &hml LGUI T        &hml LSHFT H     &kp K
#define HDP_LB      &kp F            &kp P            &kp D              &kp L            &kp X

//                  RT0              RT1              RT2                RT3              RT4
#define HDP_RT      &kp HASH         &hmr MEH DOT     &hmr HYPER FSLH    &kp DQT          &kp SQT
#define HDP_RM      &kp COMMA        &hmr RSHFT A     &hmr RGUI E        &hmr RALT I      &hmr RCTRL C
#define HDP_RB      &kp MINUS        &kp U            &kp O              &kp Y            &kp B

/*
 * Option-A thumbs (HDP-defs.h:74-82): the left hand is identical to Colemak, and
 * only R on the inner right (Promethium's signature) and Enter on the outer right
 * differ. Del is not on a thumb here — it comes from Shift+Backspace.
 */
//                  LH2              LH1                LH0
#define HDP_LH      &lt_t l_med ESC  &lt_t l_nav SPACE  &lt_t l_mos TAB
//                  RH0              RH1                RH2
#define HDP_RH      &lt_t l_sym R    &lt_bspc l_num 0   &lt_t l_fun RET

// the two keys the Totem gains over the Corne
#define HDP_LB5     &sk LSHFT
#define HDP_RB5     &key_repeat
