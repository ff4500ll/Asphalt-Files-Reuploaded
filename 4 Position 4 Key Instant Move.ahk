#NoEnv
#SingleInstance Force
SetBatchLines, -1

pos1X := ""
pos1Y := ""
pos2X := ""
pos2Y := ""
pos3X := ""
pos3Y := ""
pos4X := ""
pos4Y := ""

; Save position 1 with H
H::
    MouseGetPos, pos1X, pos1Y
    ToolTip, Position 1 saved at X: %pos1X% Y: %pos1Y%
    SetTimer, RemoveToolTip, -1500
return

; Save position 2 with J
J::
    MouseGetPos, pos2X, pos2Y
    ToolTip, Position 2 saved at X: %pos2X% Y: %pos2Y%
    SetTimer, RemoveToolTip, -1500
return

; Save position 3 with K
K::
    MouseGetPos, pos3X, pos3Y
    ToolTip, Position 3 saved at X: %pos3X% Y: %pos3Y%
    SetTimer, RemoveToolTip, -1500
return

; Save position 4 with L
L::
    MouseGetPos, pos4X, pos4Y
    ToolTip, Position 4 saved at X: %pos4X% Y: %pos4Y%
    SetTimer, RemoveToolTip, -1500
return

; Move mouse to position 1 with U
U::
    if (pos1X != "" && pos1Y != "")
        MouseMove, %pos1X%, %pos1Y%, 0
    else
    {
        ToolTip, Position 1 not saved yet. Press H to save.
        SetTimer, RemoveToolTip, -1500
    }
return

; Move mouse to position 2 with I
I::
    if (pos2X != "" && pos2Y != "")
        MouseMove, %pos2X%, %pos2Y%, 0
    else
    {
        ToolTip, Position 2 not saved yet. Press J to save.
        SetTimer, RemoveToolTip, -1500
    }
return

; Move mouse to position 3 with O
O::
    if (pos3X != "" && pos3Y != "")
        MouseMove, %pos3X%, %pos3Y%, 0
    else
    {
        ToolTip, Position 3 not saved yet. Press K to save.
        SetTimer, RemoveToolTip, -1500
    }
return

; Move mouse to position 4 with P
P::
    if (pos4X != "" && pos4Y != "")
        MouseMove, %pos4X%, %pos4Y%, 0
    else
    {
        ToolTip, Position 4 not saved yet. Press L to save.
        SetTimer, RemoveToolTip, -1500
    }
return

RemoveToolTip:
    ToolTip
return
