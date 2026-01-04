#ifWinActive, Roblox
on = false
setkeydelay, 0
SetMouseDelay, 0

Dagger = 1
Ethereal = 2
Shadow = 3
Triple = 4
Lethal = 5
Falling = 8
Throw = 6
Armis = 7
Flash = 0

$e::
settimer, spam, 10
send %Throw%
sleep 50
send %Triple%
sleep 50
send %Throw%
sleep 50
send %Lethal%
sleep 500
send %Falling%
sleep 50
send %Shadow%
sleep 100
send %Falling%
sleep 200
send %Shadow%
sleep 200
send %Dagger%
settimer, spam, off
return

spam:
send {lbutton down}
sleep 5
send {lbutton up}
return

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
settimer, nigger, 10
keywait mbutton
settimer, nigger, off
return

nigger:
send {lbutton down}
sleep 10
send {lbutton up}
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

$xbutton2::
send {g down}
send {rbutton}
sleep 100
send {f down}
sleep 500
send {f up}
send {g up}
return

$xbutton1::
send %Armis%
send {g down}
sleep 100
send {g up}
sleep 20
send {rbutton down}
sleep 20
send {rbutton up}
sleep 20
send {rbutton down}
sleep 20
send {rbutton up}
sleep 20
send {rbutton down}
sleep 20
send {rbutton up}
sleep 20
send {lbutton down}
sleep 20
send %Dagger%
sleep 20
send {lbutton up}
sleep 20
send {f down}
sleep 500
send {f up}
return