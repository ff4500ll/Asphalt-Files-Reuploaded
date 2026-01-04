#maxhotkeysperinterval 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
#ifWinActive, Roblox


selected = no
selected2 = no
cooldown = no
cooldown2 = no
ToolTip, Done, 303, 620, 1
ToolTip, Done, 951, 620, 2

~$1::
~$3::
~$4::
~$5::
~$6::
~$7::
selected = no
selected2 = no
return

$z::
send 9
selected = no
selected2 = no
return
$x::
send 0
selected = no
selected2 = no
return
$c::
send {=}
selected = no
selected2 = no
return
$t::
send 8
selected = no
selected2 = no
return

~$lbutton::
if selected = yes
	{
	if cooldown = no
		{
		cooldown := yes
		count := 0
		tooltip, 16, 303, 620, 1
		settimer, timer1, 1000
		}
	}
if selected2 = yes
	{
	if cooldown2 = no
		{
		settimer, timer1, off
		cooldown = no
		cooldown2 := yes
		count2 := 0
		tooltip, Done, 303, 620, 1
		tooltip, 31, 951, 620, 2
		settimer, timer2, 1000
		}
	}
return

~$2::
selected2 = no
if selected = no
	{
	selected = yes
	}
else
	{
	selected = no
	}
return

$r::
send -
selected = no
if selected2 = no
	{
	selected2 = yes
	}
else
	{
	selected2 = no
	}
return


timer1:
count++
display := 16-count
if display = 0
{
settimer, timer1, off
tooltip, Done, 303, 620, 1
cooldown = no
return
}
tooltip, %display%, 303, 620, 1
return

timer2:
count2++
display2 := 31-count2
if display2 < 0
{
settimer, timer2, off
tooltip, Done, 951, 620, 2
cooldown2 = no
return
}
tooltip, %display2%, 951, 620, 2
return

$mbutton::
send {' down}
send {' up}
keywait mbutton
send {' down}
send {' up}
return

$xbutton2::
send {f down}
send {space}
return

$xbutton1::
send {g up}
send {w up}
send {w down}
send {w up}
send {lbutton}
send {w down}
return

,:: suspend
return