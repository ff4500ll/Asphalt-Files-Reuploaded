#ifWinActive, Roblox ; focus roblox
setkeydelay, 0
setmousedelay, 0

Sword = 1
Action = -
WhiteFire = 5
Ice = 6
Charged = 2
Flame = 4
Pommel = 7
Thunder = 3

$r::
send %Flame%{click}
sleep 10
settimer, click, 10
sleep 10
send %Action%{click}
sleep 10
send %Sword%
sleep 600
settimer, click, off
send %Sword%
sleep 100
send {w down}
sleep 100
send {w up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 600, "UInt", 0)
send {a down}
sleep 200
settimer, click, 10
sleep 100
DllCall("mouse_event", "UInt", 0x01, "UInt", -600, "UInt", 0)
send {a up}
send %Ice%{click}
sleep 50
send %Sword%
sleep 700
send %Pommel%{click}
sleep 50
send %WhiteFire%{click}
sleep 50
send %Charged%{click}
sleep 6969696969
return

$r up::
settimer, click, off
send {a up}
reload
return

click:
send {lbutton down}
sleep 5
send {lbutton up}
return

$m:: reload
