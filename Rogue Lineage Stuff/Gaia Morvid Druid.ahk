#ifWinActive, Roblox ; focus roblox
on = false
setkeydelay, 0
setmousedelay, 0

Sword = 1
Action = 3
Pommel = 6

$z::9
return
$x::0
return
$r::-
return
$c::=
return
$t::8
return

$q:: ; auto dash
settimer, dash, 100
gosub, dash
return
$q up::
settimer, dash, off
send {q up}
return
dash:
send {q down}
sleep 50
send {q up}
return

~$/:: ; chat pause
if on = false
{
on = true
suspend, on
}
return

~$esc::
~$enter:: ; chat unpause
suspend, off
on = false
return

$mbutton:: ; autoclicker
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton2 up::
settimer, click, off
send {s up}
reload
return

$xbutton2:: ; action surge macro
send %Action%{click}
sleep 10
settimer, click, 10
sleep 10
send %Sword%
sleep 600

settimer, click, off
send %Sword%
sleep 100
send {w down}
sleep 100
send {w up}
DllCall("mouse_event", "UInt", 0x01, "UInt", 1430, "UInt", 0)
send {s down}
sleep 200
settimer, click, 10
sleep 200
DllCall("mouse_event", "UInt", 0x01, "UInt", -1430, "UInt", 0)
send {s up}
sleep 50
send %Sword%
sleep 6969696969
return

click:
send {lbutton down}
sleep 5
send {lbutton up}
return

$xbutton1:: ; spell run
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return

,:: suspend ; default suspend key