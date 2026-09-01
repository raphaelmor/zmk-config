/*
 * keynames_totem.h
 *
 * SPDX-License-Identifier: MIT
 *
 * Key position names for the TOTEM (38 keys, 3x5+3 per side plus one outer
 * pinky key per side on the bottom row).
 *
 * WHY THESE NAMES
 *   They are the same names the QMK userspace uses (users/raphaelmor/layers/
 *   HDP-defs.h) and the same ones moutis uses in his ZMK config
 *   (config/keymaps/keynames_3x5_3.h). Combo definitions therefore move between
 *   the three by name, and only the numbers below change per board.
 *
 * WHERE THE NUMBERS COME FROM
 *   The order of entries in the shield's matrix transform, at
 *   boards/shields/totem/totem.dtsi in the zmk-keyboard-totem module:
 *
 *           RC(0,0..4)          RC(0,5..9)              ->  0..4    5..9
 *           RC(1,0..4)          RC(1,5..9)              -> 10..14  15..19
 *   RC(3,0) RC(2,0..4)          RC(2,5..9)  RC(3,9)     -> 20  21..25  26..30  31
 *           RC(3,2..4)          RC(3,5..7)              -> 32..34  35..37
 *
 *   Note that row 3 does double duty: RC(3,0) and RC(3,9) are the two outer
 *   pinky keys, RC(3,2..7) are the six thumbs, and RC(3,1)/RC(3,8) are unused
 *   matrix intersections.
 *
 *                        TOTEM KEY POSITION NAMES
 *
 *       ╭─────────────────────────╮      ╭─────────────────────────╮
 *       │ LT4 LT3 LT2 LT1 LT0     │      │     RT0 RT1 RT2 RT3 RT4 │
 *       │ LM4 LM3 LM2 LM1 LM0     │      │     RM0 RM1 RM2 RM3 RM4 │
 *  LB5  │ LB4 LB3 LB2 LB1 LB0     │      │     RB0 RB1 RB2 RB3 RB4 │  RB5
 *       ╰───────────╮ LH2 LH1 LH0 │      │ RH0 RH1 RH2 ╭───────────╯
 *                   ╰─────────────╯      ╰─────────────╯
 *
 *  DIFFERENCE FROM THE CORNE
 *    The QMK keymap is a 3x6+3 with two extra keys per side. On the Hands Down
 *    base its outer columns (LT5 LM5 LB5 and mirrors) and its four "ex2" keys
 *    (LTA LMA RTA RMA) are all KC_NO, so the live grid is exactly this one.
 *    LB5 and RB5 are the only positions here that had no counterpart, and they
 *    are new keys rather than replacements.
 */

#pragma once

// top row
#define LT4  0
#define LT3  1
#define LT2  2
#define LT1  3
#define LT0  4

#define RT0  5
#define RT1  6
#define RT2  7
#define RT3  8
#define RT4  9

// home row
#define LM4 10
#define LM3 11
#define LM2 12
#define LM1 13
#define LM0 14

#define RM0 15
#define RM1 16
#define RM2 17
#define RM3 18
#define RM4 19

// bottom row, including the two outer pinky keys
#define LB5 20
#define LB4 21
#define LB3 22
#define LB2 23
#define LB1 24
#define LB0 25

#define RB0 26
#define RB1 27
#define RB2 28
#define RB3 29
#define RB4 30
#define RB5 31

// thumbs
#define LH2 32
#define LH1 33
#define LH0 34

#define RH0 35
#define RH1 36
#define RH2 37

/*
 * Hand and thumb groups.
 *
 * These feed hold-trigger-key-positions on the home-row mods, which is ZMK's
 * native equivalent of QMK's CHORDAL_HOLD: a left-hand mod only takes its hold
 * if the next key is on the right hand or a thumb. THUMBS is included on both
 * sides on purpose, so chords like Shift+Space keep working.
 */
#define KEYS_L LT4 LT3 LT2 LT1 LT0  LM4 LM3 LM2 LM1 LM0  LB5 LB4 LB3 LB2 LB1 LB0
#define KEYS_R RT0 RT1 RT2 RT3 RT4  RM0 RM1 RM2 RM3 RM4  RB0 RB1 RB2 RB3 RB4 RB5

#define THUMBS_L LH2 LH1 LH0
#define THUMBS_R RH0 RH1 RH2
#define THUMBS   THUMBS_L THUMBS_R
