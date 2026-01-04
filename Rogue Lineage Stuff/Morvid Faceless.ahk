#ifWinActive, Roblox
on = false
setkeydelay, 0
SetMouseDelay, 0

Lethal = 5
Triple = 4
Shadow = 3
Dagger = 1

~$/:: ; chat pause
if on = false
{
on = true
suspend, on
}
return

~$esc:: ; chat unpause
~$enter::
suspend, off
on = false
return

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
$y::e
return

$mbutton::
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$q:: ; auto dash
settimer, dash, 100
gosub, dash
return
$q up::
settimer, dash, off
return
dash:
send {q}
return

$,:: suspend
return

$e::
send %Lethal%
sleep 50
send %Lethal%
sleep 250
send %Lethal%
settimer, NIGGER, 20
sleep 50
send %Triple%
sleep 200
send %Shadow%
sleep 200
settimer, NIGGER, off
sleep 200
send %Dagger%
return

NIGGER:
send {lbutton down}
sleep 10
send {lbutton up}
return

$xbutton2::
send {g down}
send {rbutton}
sleep 100
send {f down}
sleep 500
send {f up}
send {g up}
return

$xbutton1:: ; spell run
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return