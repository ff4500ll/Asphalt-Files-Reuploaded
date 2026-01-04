#ifWinActive, Roblox ; focus roblox
on = false

$z::7
return
$x::8
return
$r::9
return
$c::0
return
$t::6
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

,:: suspend ; default suspend key