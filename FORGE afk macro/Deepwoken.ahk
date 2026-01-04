; ========================================
; ROBLOX MACRO SCRIPT
; Only active when Roblox window is focused
; ========================================

#ifWinActive, Roblox
#MaxHotkeysPerInterval 999999999

; Performance settings for maximum speed
SetKeyDelay, -1
SetMouseDelay, -1
SetBatchLines, -1

; Global pause state
isPaused := 0


; ========================================
; MOUSE BUTTON REMAPPING
; ========================================

; Side mouse button 1 → Press 0
$xbutton1::0

; Side mouse button 2 → Press 9
$xbutton2::9


; ========================================
; J KEY: Q + SPACE SPAM
; Hold J to repeatedly press Q and Space
; Timing: 2.1 second intervals
; ========================================

$j::
    SetTimer, JSpam, 2100
    gosub, JSpam
return

$j up::
    SetTimer, JSpam, Off
return

JSpam:
    GetKeyState, jstate, j, p
    if (jstate = "U") {
        SetTimer, JSpam, Off
        return
    }
    Send, {q down}
    Sleep, 5
    Send, {space down}
    Sleep, 10
    Send, {q up}
    Send, {space up}
return


; ========================================
; MIDDLE MOUSE BUTTON: COMBAT COMBO
; Right-click + Ctrl+Left-click spam
; Releases W key first
; Timing: 50ms intervals
; ========================================

$mbutton::
    Send, {w up}
    SetTimer, MbuttonSpam, 50
    gosub, MbuttonSpam
return

$mbutton up::
    SetTimer, MbuttonSpam, Off
return

MbuttonSpam:
    GetKeyState, mbstate, mbutton, p
    if (mbstate = "U") {
        SetTimer, MbuttonSpam, Off
        return
    }
    Send, {rbutton down}
    Sleep, 5
    Send, {rbutton up}
    Sleep, 5
    Send, {ctrl down}
    Sleep, 5
    Send, {lbutton down}
    Sleep, 5
    Send, {lbutton up}
    Send, {ctrl up}
return


; ========================================
; UTILITY HOTKEYS
; ========================================

; L → Reload entire script
$l::reload

; Z → Press 7
$z::7

; X → Press 8
$x::8


; ========================================
; PAUSE/UNPAUSE SYSTEM
; ========================================

; TAB or / → Toggle pause (shows tooltip)
~$tab::
~$/:
    isPaused := !isPaused
    if (isPaused) {
        ToolTip, Paused
        Suspend, On
    } else {
        ToolTip
        Suspend, Off
    }
return

; ESC or ENTER → Force unpause
~$esc::
~$enter::
    isPaused := 0
    ToolTip
    Suspend, Off
return


; ========================================
; LEFT CLICK: AUTO-CLICKER
; Hold left mouse button for rapid clicks
; Timing: 50ms intervals (20 clicks/sec)
; ========================================

$lbutton::
    SetTimer, PerformClick, 50
    gosub, PerformClick
return

$lbutton up::
    SetTimer, PerformClick, Off
return

PerformClick:
    GetKeyState, buttonState, lbutton, p
    if (buttonState = "U") {
        SetTimer, PerformClick, Off
        return
    }
    Send, {lbutton down}
    Sleep, 5
    Send, {lbutton up}
return


; ========================================
; Q KEY: Q SPAM
; Hold Q to repeatedly press it
; Timing: 100ms intervals (10 presses/sec)
; ========================================

*$q::
    SetTimer, QSpam, 100
    gosub, QSpam
return

$q up::
    SetTimer, QSpam, Off
return

QSpam:
    GetKeyState, qstate, q, p
    if (qstate = "U") {
        SetTimer, QSpam, Off
        return
    }
    Send, {q down}
    Sleep, 50
    Send, {q up}
return


; ========================================
; EMERGENCY SUSPEND
; ========================================

; COMMA → Suspend all hotkeys
,::suspend
return