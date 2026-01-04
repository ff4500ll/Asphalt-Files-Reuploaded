#SingleInstance Force
#IfWinActive, ahk_exe RobloxPlayerBeta.exe

setkeydelay, -1
setbatchlines, -1

$y::;
$xbutton1::=
$xbutton2::-

$/::
send {/ down}
keywait /
send {/ up}
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

$,::
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

~$esc::
~$enter::
suspend, off
pause := false
tooltip
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

$t::
if (!t)
{
t := true
settimer, t, 100
send {t down}
sleep 50
send {t up}
}
return
$t up::
t := false
settimer, t, off
return
t:
send {t down}
sleep 50
send {t up}
if not getkeystate("t", "p")
settimer, t, off
return

$z::
if (!z)
{
z := true
settimer, z, 100
send {z down}
sleep 50
send {z up}
}
return
$z up::
z := false
settimer, z, off
return
z:
send {z down}
sleep 50
send {z up}
if not getkeystate("z", "p")
settimer, z, off
return

$x::
if (!x)
{
x := true
settimer, x, 100
send {x down}
sleep 50
send {x up}
}
return
$x up::
x := false
settimer, x, off
return
x:
send {x down}
sleep 50
send {x up}
if not getkeystate("x", "p")
settimer, x, off
return

$c::
if (!c)
{
c := true
settimer, c, 100
send {c down}
sleep 50
send {c up}
}
return
$c up::
c := false
settimer, c, off
return
c:
send {c down}
sleep 50
send {c up}
if not getkeystate("c", "p")
settimer, c, off
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

$5::
if (!5a)
{
5a := true
settimer, 5a, 100
send {5 down}
sleep 50
send {5 up}
}
return
$5 up::
5a := false
settimer, 5a, off
return
5a:
send {5 down}
sleep 50
send {5 up}
if not getkeystate("5", "p")
settimer, 5a, off
return

$6::
if (!6a)
{
6a := true
settimer, 6a, 100
send {6 down}
sleep 50
send {6 up}
}
return
$6 up::
6a := false
settimer, 6a, off
return
6a:
send {6 down}
sleep 50
send {6 up}
if not getkeystate("6", "p")
settimer, 6a, off
return