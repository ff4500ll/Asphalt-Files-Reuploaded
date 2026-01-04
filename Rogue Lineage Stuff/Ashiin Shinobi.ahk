#ifWinActive, Roblox ; focus roblox
on = false
setkeydelay, 0

Shoulder = -
Triple = 5
Owl = 3
Shadow = 4

r::
settimer, spam, 10
send %Triple%
sleep 50
send %Shoulder%
sleep 50
send %Owl%
sleep 500
send %Shadow%
sleep 100
settimer, spam, off
return

spam:
send {lbutton down}
sleep 5
send {lbutton up}
return

$z::9
return
$x::0
return
$c::=
return
$t::8
return
$r::-
return

~$/:: ; chat pause
if on = false
{
on = true
tooltip, macro paused ah just saying
suspend, on
}
return

~$esc::
~$enter:: ; chat unpause
suspend, off
tooltip
on = false
return

$mbutton:: ; autoclicker
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton2:: ; snap ignis shield
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
send {lbutton}
send {w up}
send {w down}
return

,:: suspend ; default suspend key