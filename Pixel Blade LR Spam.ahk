#NoEnv
#SingleInstance Force
SetKeyDelay, -1
SetBatchLines, -1
SetMouseDelay, -1

spam := false
pressTime := 0
isPressed := false

$,::
    Suspend
    if (A_IsSuspended) {
        ToolTip, Script SUSPENDED
        SetTimer, ClearToolTip, -2000
    } else {
        ToolTip, Script ACTIVE
        SetTimer, ClearToolTip, -2000
    }
return

#IfWinActive, Roblox

$xbutton1::
$xbutton2::
    ToggleSpam()
return

$MButton::
    SetTimer, MSpamLoop, 10
return

$MButton Up::
    SetTimer, MSpamLoop, Off
    Send {LButton up}
return

$LButton::
    global spam
    if (spam) {
        SetTimer, MSpamLoop, 10
    } else {
        Send {LButton down}
    }
return

$LButton Up::
    global spam
    if (spam) {
        SetTimer, MSpamLoop, Off
        Send {LButton up}
    } else {
        Send {LButton up}
    }
return

$e::
    SetTimer, ESpamLoop, 10
return

$e Up::
    SetTimer, ESpamLoop, Off
return

#IfWinActive

ToggleSpam() {
    global spam, isPressed, pressTime
    spam := !spam
    
    if (spam) {
        ToolTip, RButton Spam: ON
        isPressed := false
        pressTime := 0
        SetTimer, FastSpamLoop, 1
    } else {
        ToolTip, RButton Spam: OFF
        SetTimer, FastSpamLoop, Off
        Send {RButton up}
        SetTimer, ClearToolTip, -2000
    }
}

FastSpamLoop:
    global spam, pressTime, isPressed
    
    if (!spam) {
        isPressed := false
        pressTime := 0
        return
    }
    
    currentTime := A_TickCount
    
    if (!isPressed) {
        Send {RButton down}
        isPressed := true
        pressTime := currentTime
    } else if (currentTime - pressTime >= 500) {
        Send {RButton up}
        isPressed := false
    }
return

MSpamLoop:
    Click
return

ESpamLoop:
    Send e
return

ClearToolTip:
    ToolTip
return

$r::Reload
$z::e