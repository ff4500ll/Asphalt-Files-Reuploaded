#ifWinActive, Roblox ; focus roblox
on = false
setkeydelay, 0

Rising = 6
Cruel = 5
Owl = 3
Shadow = 4

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

$xbutton2:: ; snap ignis
send {g down}
send {rbutton}
sleep 150
send {f down}
sleep 500
send {f up}
send {g up}
return

$r::
send %Owl%{click}
sleep 50
send %Cruel%{click}
sleep 50
send %Rising%{click}
sleep 100
send %Shadow%{click}
sleep 400
send %Cruel%{click}
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