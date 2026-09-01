/*
 * layers_def.h — the six non-alpha layers
 *
 * SPDX-License-Identifier: MIT
 *
 * Ported from users/raphaelmor/layers/{MED,NAV,MOS,SYM,NUM,FUN}-defs.h.
 * Shared by both bases, exactly as in QMK.
 *
 * DROPPED: every *_RGB_* define, roughly 500 of them across the nine QMK layer
 * files, plus ramo_ledmap.c. The Totem has no LEDs, no display and no encoders —
 * grepping the whole shield for led|rgb|ws2812|display finds nothing but
 * display-name strings. This also makes the encoder-versus-OLED pin conflict at
 * QMK-feature-audit.md:254-262 moot.
 *
 * DROPPED: the LT5/LM5/RT5/RM5 outer-column and LTA/LMA/RTA/RMA ex2 positions.
 * All were KC_NO. The Totem has no counterpart for them.
 *
 * LB5 and RB5 are &trans on every layer here, so the base layer's sticky shift
 * and key repeat stay reachable. MED's LB5 is the one exception.
 *
 * Each layer keeps QMK's arrangement: the payload sits on the hand opposite the
 * thumb that activates the layer, with a modifier block on the activating hand.
 */

#pragma once

/*
 * MEDIA — activated by the left Esc thumb.
 *
 * The one layer that genuinely changes. QMK's top-right row was RGB control
 * (MED-defs.h:29-33: RM_TOGG RM_NEXT RM_HUEU RM_SATU RM_VALU) and has no target
 * on this board. It becomes what a wireless split actually needs: Bluetooth
 * profile select, clear bonds, and the USB/BLE output toggle.
 *
 * THE BLUETOOTH CONTROLS ARE MIRRORED ONTO BOTH HALVES, ON PURPOSE.
 *   The layer is activated by a LEFT thumb, so the left-hand copy is reachable
 *   with the left half alone. That matters because the moment you need BT_CLR is
 *   the moment the two halves are not talking to each other — and a right-hand-only
 *   copy is unreachable precisely then. The validation keymap this replaced made
 *   the same choice for the same reason ("Both reach the same layer, so it works
 *   with one half alone").
 *
 *   Left half, reading outer to inner:  OUT_TOG  BT_CLR  BT_SEL2  BT_SEL1  BT_SEL0
 *   Right half, reading inner to outer: BT_SEL0  BT_SEL1  BT_SEL2  BT_CLR  OUT_TOG
 *   So the two copies are spatial mirrors of each other.
 *
 * Reset and bootloader go on the outer pinky key, which QMK-feature-audit.md:250
 * notes exist on no layer at all in the QMK build. Reaching them needs the Esc
 * thumb plus the far outer key, which is deliberate enough to be safe. The XIAO's
 * double-tap-reset remains the reliable path if firmware is misbehaving.
 */
#define l_med_label "MEDIA"

//                  LT4              LT3              LT2              LT1              LT0
#define l_med_LT    &out OUT_TOG     &bt BT_CLR       &bt BT_SEL 2     &bt BT_SEL 1     &bt BT_SEL 0
#define l_med_LM    &kp LCTRL        &kp LALT         &kp LGUI         &kp LSHFT        &none
#define l_med_LB    &none            &none            &kp RALT         &none            &none

//                  RT0              RT1              RT2              RT3              RT4
#define l_med_RT    &bt BT_SEL 0     &bt BT_SEL 1     &bt BT_SEL 2     &bt BT_CLR       &out OUT_TOG
#define l_med_RM    &none            &kp C_PREV       &kp C_VOL_DN     &kp C_VOL_UP     &kp C_NEXT
#define l_med_RB    &none            &none            &none            &none            &none

#define l_med_LH    &trans           &none            &none
#define l_med_RH    &kp C_STOP       &kp C_PP         &kp C_MUTE

#define l_med_LB5   &rst_btld 0 0
#define l_med_RB5   &trans

/*
 * NAV — activated by the left Space thumb.
 *
 * Carries the two base-layer switches (NAV-defs.h:23-24). Double-tap required, so
 * a stray press cannot change your base.
 */
#define l_nav_label "NAV"

//                  LT4              LT3              LT2              LT1              LT0
#define l_nav_LT    &none            &none            &td_cmk          &td_hdp          &none
#define l_nav_LM    &kp LCTRL        &kp LALT         &kp LGUI         &kp LSHFT        &none
#define l_nav_LB    &none            &none            &kp RALT         &none            &none

//                  RT0              RT1              RT2              RT3              RT4
#define l_nav_RT    &kp LG(Z)        &kp LG(V)        &kp LG(C)        &kp LG(X)        &kp LS(LG(Z))
#define l_nav_RM    &caps_word       &kp LEFT         &kp DOWN         &kp UP           &kp RIGHT
#define l_nav_RB    &kp INS          &kp HOME         &kp PG_DN        &kp PG_UP        &kp END

#define l_nav_LH    &none            &trans           &none
#define l_nav_RH    &kp RET          &kp BSPC         &kp DEL

#define l_nav_LB5   &trans
#define l_nav_RB5   &trans

/*
 * MOUSE — activated by the left Tab thumb.
 *
 * Movement and scroll tuning is on &mmv / &msc in ramo_config.dtsi, ported from
 * QMK's MOUSEKEY_* values. Needs CONFIG_ZMK_POINTING=y.
 *
 * Note the clipboard row is ordered differently from NAV's, mirroring
 * MOS-defs.h:28-32 — undo and redo are swapped relative to NAV-defs.h:29-33.
 */
#define l_mos_label "MOUSE"

//                  LT4              LT3              LT2              LT1              LT0
#define l_mos_LT    &none            &none            &none            &none            &none
#define l_mos_LM    &kp LCTRL        &kp LALT         &kp LGUI         &kp LSHFT        &none
#define l_mos_LB    &none            &none            &kp RALT         &none            &none

//                  RT0              RT1              RT2              RT3              RT4
#define l_mos_RT    &kp LS(LG(Z))    &kp LG(V)        &kp LG(C)        &kp LG(X)        &kp LG(Z)
#define l_mos_RM    &none            &mmv MOVE_LEFT   &mmv MOVE_DOWN   &mmv MOVE_UP     &mmv MOVE_RIGHT
#define l_mos_RB    &none            &msc SCRL_LEFT   &msc SCRL_DOWN   &msc SCRL_UP     &msc SCRL_RIGHT

#define l_mos_LH    &none            &none            &trans
#define l_mos_RH    &mkp RCLK        &mkp LCLK        &mkp MCLK

#define l_mos_LB5   &trans
#define l_mos_RB5   &trans

/*
 * SYM — activated by the right R thumb on Hands Down, the right Enter thumb on
 * Colemak.
 *
 * The two opening brackets are linger keys: tap for the bracket, hold past
 * my_linger_term for the pair with the caret between (replacing ramo_linger.c).
 * The first parameter goes to the 0-cell pair macro and must be 0.
 *
 * HDPM-parity.md:239 flags that "[" has no home on any layer and that a
 * programming-oriented SYM v2 is the intended follow-up. Left as-is here: this
 * port matches the QMK layout rather than extending it.
 */
#define l_sym_label "SYM"

//                  LT4              LT3              LT2              LT1              LT0
#define l_sym_LT    &lk_brc 0 LBRC   &kp AMPS         &kp STAR         &lk_par 0 LPAR   &kp RBRC
#define l_sym_LM    &kp COLON        &kp DLLR         &kp PRCNT        &kp CARET        &kp PLUS
#define l_sym_LB    &kp TILDE        &kp EXCL         &kp AT           &kp HASH         &kp PIPE

//                  RT0              RT1              RT2              RT3              RT4
#define l_sym_RT    &none            &none            &none            &none            &none
#define l_sym_RM    &none            &kp RSHFT        &kp RGUI         &kp RALT         &kp RCTRL
#define l_sym_RB    &none            &none            &none            &kp RALT         &none

#define l_sym_LH    &lk_par 0 LPAR   &kp RPAR         &kp UNDER
#define l_sym_RH    &trans           &none            &none

#define l_sym_LB5   &trans
#define l_sym_RB5   &trans

/*
 * NUM — activated by the right Backspace thumb.
 */
#define l_num_label "NUM"

//                  LT4              LT3              LT2              LT1              LT0
#define l_num_LT    &kp LBKT         &kp N7           &kp N8           &kp N9           &kp RBKT
#define l_num_LM    &kp SEMI         &kp N4           &kp N5           &kp N6           &kp EQUAL
#define l_num_LB    &kp GRAVE        &kp N1           &kp N2           &kp N3           &kp BSLH

//                  RT0              RT1              RT2              RT3              RT4
#define l_num_RT    &none            &none            &none            &none            &none
#define l_num_RM    &none            &kp RSHFT        &kp RGUI         &kp RALT         &kp RCTRL
#define l_num_RB    &none            &none            &none            &kp RALT         &none

#define l_num_LH    &kp DOT          &kp N0           &kp MINUS
#define l_num_RH    &none            &trans           &none

#define l_num_LB5   &trans
#define l_num_RB5   &trans

/*
 * FUN — activated by the right Enter thumb on Hands Down, the right Del thumb on
 * Colemak.
 */
#define l_fun_label "FUN"

//                  LT4              LT3              LT2              LT1              LT0
#define l_fun_LT    &kp F12          &kp F7           &kp F8           &kp F9           &kp PSCRN
#define l_fun_LM    &kp F11          &kp F4           &kp F5           &kp F6           &kp SLCK
#define l_fun_LB    &kp F10          &kp F1           &kp F2           &kp F3           &kp PAUSE_BREAK

//                  RT0              RT1              RT2              RT3              RT4
#define l_fun_RT    &none            &none            &none            &none            &none
#define l_fun_RM    &none            &kp RSHFT        &kp RGUI         &kp RALT         &kp RCTRL
#define l_fun_RB    &none            &none            &none            &kp RALT         &none

#define l_fun_LH    &kp K_APP        &kp SPACE        &kp TAB
#define l_fun_RH    &none            &none            &trans

#define l_fun_LB5   &trans
#define l_fun_RB5   &trans
