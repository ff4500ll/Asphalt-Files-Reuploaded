#ifWinActive, Roblox

$mbutton::
Tooltip, Autoclicker
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
Tooltip
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
~$enter::
suspend, off
tooltip
on = false
return

$xbutton1::
Tooltip, qer
while getkeystate("xbutton1","P")
{
send q
sleep 10
send e
sleep 10
send r
}
keywait xbutton1
Tooltip
return

$e::
Tooltip, e
while getkeystate("e","P")
{
send e
}
keywait e
Tooltip
return

$q::
Tooltip, q
while getkeystate("q","P")
{
send q
}
keywait q
Tooltip
return

$r::
Tooltip, r
while getkeystate("r","P")
{
send r
}
keywait r
Tooltip
return

$xbutton2::
Tooltip, Reloaded
reload
return