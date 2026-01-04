#MaxHotkeysPerInterval 2000000000000000000
setkeydelay 0

on = false
hold = false

~2::
~3::
~4::
~5::
~6::
~r::
~t::
~f::
send {lbutton up}
sleep 5
send {rbutton down}
sleep 10
send {rbutton up}
sleep 10
send {q down}
sleep 10
send {q up}
sleep 10
send {1 down}
sleep 10
send {1 up}
sleep 5
if hold = true
send {lbutton down}
return

~$lbutton::
hold = true
return

~$lbutton up::
hold = false
return

$q::
while getkeystate("q","P")
{
send q
sleep 5
}
return

~$i::
~$/::
if on = false
{
on = true
suspend, on
}
return

~$esc::
~$enter::
suspend, off
on = false
return