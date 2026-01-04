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

$r::
Tooltip, Loop Waiting
send q
sleep 10 ;important
Tooltip, Loop Enabled
SetTimer, RemoveToolTip, -2000
loop,
{
send q
send e
}
return

$xbutton1::
Tooltip, q+e
while getkeystate("xbutton1","P")
{
send q
send e
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

$xbutton2::
Tooltip, Reloaded
reload
return

ScriptStat := false
$,::
	Suspend
	If ScriptStat
	{
		ScriptStat := false
		Tooltip, Script Enabled
		SetTimer, RemoveToolTip, -1000
		Suspend, Off
	} else {
		ScriptStat := true
		Tooltip, Script Paused
		Suspend, On
	}
return

RemoveToolTip:
SetTimer, RemoveToolTip, off
ToolTip
return