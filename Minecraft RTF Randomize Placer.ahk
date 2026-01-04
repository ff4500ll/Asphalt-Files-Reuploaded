; --- SETTINGS ---
ratioR := 65   ; % chance for R
ratioT := 25   ; % chance for T
ratioF := 10   ; % chance for F

paused := false

; --- TOGGLE PAUSE WITH XBUTTON1 ---
XButton1::
    paused := !paused
    if (paused)
        ToolTip, Script Paused
    else
        ToolTip, Script Active
    SetTimer, RemoveTooltip, -1000
return

RemoveTooltip:
    ToolTip
return

; --- RIGHT CLICK TRIGGER ---
~*RButton::
    if (paused)
        return
    
    Random, roll, 1, 100

    if (roll <= ratioR) {
        Send, {r}
    } else if (roll <= ratioR + ratioT) {
        Send, {t}
    } else {
        Send, {f}
    }
return
