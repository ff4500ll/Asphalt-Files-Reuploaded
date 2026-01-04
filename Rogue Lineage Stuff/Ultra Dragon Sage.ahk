#ifWinActive, Roblox ; focus roblox
setkeydelay, 0
setmousedelay, 0
on = false

Elbow = 1
Drop = -
Monastic = 4
Snarv = 8

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

~$/:: ; chat pause
if on = false
{
on = true
suspend, on
}
return

~$esc::
~*$esc::
~$enter:: ; chat unpause
~*$enter::
suspend, off
on = false
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

$mbutton:: ; autoclicker
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton1:: ; spell run
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return

$xbutton2 up::
reload
return

$xbutton2::
send %Drop%{click}
sleep 25
send %Monastic%{click}
sleep 1885
send {click}
sleep 200
send %Snarv%
sleep 200
send {click, R}
sleep 100
send %Elbow%
sleep 10
send {click}
return

$,:: suspend