/*
 * cmk-config.h — Colemak alpha rows
 *
 * SPDX-License-Identifier: MIT
 *
 * Ported from users/raphaelmor/layers/CMK-defs.h.
 *
 * This is the fallback base and ZMK's layer 0, so it is what the board comes up
 * in after a reboot or a deep-sleep wake. Double-tap the NAV tap-dance or press
 * the LB5+RB5 combo to get back to Hands Down.
 *
 *     ╭─────────────────────────╮      ╭─────────────────────────╮
 *     │  Q   W   F   P   G      │      │      J   L   U   Y   '  │
 *     │  A   R   S   T   D      │      │      H   N   E   I   O  │
 * ⇧ₛ  │  Z   X   C   V   B      │      │      K   M   ,   .   /  │  ⟳
 *     ╰───────────╮ ESC SPC TAB │      │ ENT BSP DEL ╭───────────╯
 *                 ╰─────────────╯      ╰─────────────╯
 *
 *   Same GACS home-row mods and the same Hyper/Meh placement as Hands Down.
 *
 * DROPPED IN THE PORT: the four ex2 positions (CMK-defs.h:77,79,93,95) all held
 * a second copy of LCTL_T(KC_A). QMK-feature-audit.md:120 calls them a pointless
 * duplicate. The Totem has no such positions, so they simply go away.
 */

#pragma once

#define CMK_label "Colemak"

//                  LT4              LT3              LT2                LT1              LT0
#define CMK_LT      &kp Q            &kp W            &hml HYPER F       &hml MEH P       &kp G
#define CMK_LM      &hml LCTRL A     &hml LALT R      &hml LGUI S        &hml LSHFT T     &kp D
#define CMK_LB      &kp Z            &kp X            &kp C              &kp V            &kp B

//                  RT0              RT1              RT2                RT3              RT4
#define CMK_RT      &kp J            &hmr MEH L       &hmr HYPER U       &kp Y            &kp SQT
#define CMK_RM      &kp H            &hmr RSHFT N     &hmr RGUI E        &hmr RALT I      &hmr RCTRL O
#define CMK_RB      &kp K            &kp M            &kp COMMA          &kp DOT          &kp FSLH

// Colemak keeps Del on the outer right thumb, so it needs no Shift+Bspc route —
// but lt_bspc is used anyway, so the two bases behave identically there.
//                  LH2              LH1                LH0
#define CMK_LH      &lt_t l_med ESC  &lt_t l_nav SPACE  &lt_t l_mos TAB
//                  RH0              RH1                RH2
#define CMK_RH      &lt_t l_sym RET  &lt_bspc l_num 0   &lt_t l_fun DEL

// the two keys the Totem gains over the Corne
#define CMK_LB5     &sk LSHFT
#define CMK_RB5     &key_repeat
