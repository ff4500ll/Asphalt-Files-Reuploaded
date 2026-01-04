#SingleInstance Force
SetWorkingDir %A_ScriptDir%
if not A_IsAdmin
	Run *RunAs "%A_ScriptFullPath%"

#IfWinActive, ahk_exe Client-Win64-Shipping.exe
#MaxHotkeysPerInterval 9999

setkeydelay, -1
setbatchlines, -1

$xbutton1::
suspend, off
if (!pause)
{
pause := true
tooltip, paused
suspend, on
return
}
pause := false
tooltip
return

$xbutton2::lbutton

$lbutton::
if (!lbutton)
{
lbutton := true
settimer, lbutton, 100
send {lbutton down}
sleep 50
send {lbutton up}
}
return
$lbutton up::
lbutton := false
settimer, lbutton, off
return
lbutton:
send {lbutton down}
sleep 50
send {lbutton up}
if not getkeystate("lbutton", "p")
settimer, lbutton, off
return

$rbutton::
if (!rbutton)
{
rbutton := true
settimer, rbutton, 100
send {rbutton down}
sleep 50
send {rbutton up}
}
return
$rbutton up::
rbutton := false
settimer, rbutton, off
return
rbutton:
send {rbutton down}
sleep 50
send {rbutton up}
if not getkeystate("rbutton", "p")
settimer, rbutton, off
return

$q::
if (!q)
{
q := true
settimer, q, 100
send {q down}
sleep 50
send {q up}
}
return
$q up::
q := false
settimer, q, off
return
q:
send {q down}
sleep 50
send {q up}
if not getkeystate("q", "p")
settimer, q, off
return

$e::
if (!e)
{
e := true
settimer, e, 100
send {e down}
sleep 50
send {e up}
}
return
$e up::
e := false
settimer, e, off
return
e:
send {e down}
sleep 50
send {e up}
if not getkeystate("e", "p")
settimer, e, off
return

$r::
if (!r)
{
r := true
settimer, r, 100
send {r down}
sleep 50
send {r up}
}
return
$r up::
r := false
settimer, r, off
return
r:
send {r down}
sleep 50
send {r up}
if not getkeystate("r", "p")
settimer, r, off
return

$f::
if (!f)
{
f := true
settimer, f, 100
send {f down}
sleep 50
send {f up}
}
return
$f up::
f := false
settimer, f, off
return
f:
send {f down}
sleep 50
send {f up}
if not getkeystate("f", "p")
settimer, f, off
return

$1::
if (!1a)
{
1a := true
settimer, 1a, 100
send {1 down}
sleep 50
send {1 up}
}
return
$1 up::
1a := false
settimer, 1a, off
return
1a:
send {1 down}
sleep 50
send {1 up}
if not getkeystate("1", "p")
settimer, 1a, off
return

$2::
if (!2a)
{
2a := true
settimer, 2a, 100
send {2 down}
sleep 50
send {2 up}
}
return
$2 up::
2a := false
settimer, 2a, off
return
2a:
send {2 down}
sleep 50
send {2 up}
if not getkeystate("2", "p")
settimer, 2a, off
return

$3::
if (!3a)
{
3a := true
settimer, 3a, 100
send {3 down}
sleep 50
send {3 up}
}
return
$3 up::
3a := false
settimer, 3a, off
return
3a:
send {3 down}
sleep 50
send {3 up}
if not getkeystate("3", "p")
settimer, 3a, off
return

$4::
if (!4a)
{
4a := true
settimer, 4a, 100
send {4 down}
sleep 50
send {4 up}
}
return
$4 up::
4a := false
settimer, 4a, off
return
4a:
send {4 down}
sleep 50
send {4 up}
if not getkeystate("4", "p")
settimer, 4a, off
return