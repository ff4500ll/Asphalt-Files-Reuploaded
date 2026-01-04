#ifWinActive, Roblox ; focus roblox

setkeydelay, 0
pause = off
on = false

$r:: ; m1 as many times as u want WITHOUT RAGDOLL then press key
send 4 ; triple dagger throw
sleep 100
send 5{click} ; lethality
send 4{click} ; triple dagger throw
sleep 100
send 3{click} ; shadow fan
sleep 750
send 2{click} ; ethereal strike
return

$t:: ; HOLD LETHALITY WHILE THEY ARE RAGDOLLED then press this BEFORE they get up
send {click}
sleep 200
send 4{click} ; triple dagger throw
send 3{click} ; shadow fan
sleep 500
send 2{click} ; lethality
return

$z::0 ; keybinds
return
$x::- ; keybinds
return
$c::= ; keybinds
return

$,:: suspend
return

~$`:: ; open inventory pauser
suspend, off
if pause = off
{
pause = on
tooltip, Paused
suspend, on
return
}
if pause = on
{
pause = off
tooltip
return
}
return

~$/:: ; chat pause
if on = false
{
on = true
tooltip, macro paused ah just saying
suspend, on
}
return

~$esc:: ; chat unpause
~$enter:: ; chat unpause
suspend, off
tooltip
on = false
return

$lbutton:: ; autoclicker
send {click}
settimer, wakandaforever, 50
keywait lbutton
settimer, wakandaforever, off
return
wakandaforever:
send {click}
return

$numpad3:: exitapp ; suicide button