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

/*
 * Every letter is an adaptive key (&ak_X or a hold-tap whose tap is one), which is
 * what carries the 20 Promethium adaptive rules and CommaMagic — see
 * layouts/hdp-adapt.dtsi. The letter each key types lives in that file, as the
 * adaptive's default binding, not here.
 *
 * Q and Z are the exceptions. Neither has a key on this base: Q is the W+M combo and
 * Z is the N+H combo. The Z combo binds &ak_Z so it still gets CommaMagic; Q's runs
 * through a macro, so it does not.
 *
 * HASH, DOT, FSLH, DQT, SQT, COMMA and MINUS stay plain — not letters, so no
 * adaptive rule and no CommaMagic.
 */
//                  LT4              LT3              LT2                LT1              LT0
#define HDP_LT      &ak_V            &ak_W            &mt_G HYPER G      &mt_M MEH M      &ak_J
#define HDP_LM      &mt_S LCTRL S    &mt_N LALT N     &mt_T LGUI T       &mt_H LSHFT H    &ak_K
#define HDP_LB      &ak_F            &ak_P            &ak_D              &ak_L            &ak_X

//                  RT0              RT1              RT2                RT3              RT4
#define HDP_RT      &kp HASH         &hmr MEH DOT     &hmr HYPER FSLH    &kp DQT          &kp SQT
#define HDP_RM      &kp COMMA        &mt_A RSHFT A    &mt_E RGUI E       &mt_I RALT I     &mt_C RCTRL C
#define HDP_RB      &kp MINUS        &ak_U            &ak_O              &ak_Y            &ak_B

/*
 * Option-A thumbs (HDP-defs.h:74-82): the left hand is identical to Colemak, and
 * only R on the inner right (Promethium's signature) and Enter on the outer right
 * differ. Del is not on a thumb here — it comes from Shift+Backspace.
 *
 * R uses lt_R rather than lt_t so that it, too, gets CommaMagic.
 */
//                  LH2              LH1                LH0
#define HDP_LH      &lt_t l_med ESC  &lt_t l_nav SPACE  &lt_t l_mos TAB
//                  RH0              RH1                RH2
#define HDP_RH      &lt_R l_sym R    &lt_bspc l_num 0   &lt_t l_fun RET

// the two keys the Totem gains over the Corne
#define HDP_LB5     &sk LSHFT
#define HDP_RB5     &key_repeat
