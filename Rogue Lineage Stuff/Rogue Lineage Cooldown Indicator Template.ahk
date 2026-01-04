#ifWinActive, Roblox ; focus roblox
setkeydelay, 0
setmousedelay, 0
on = false

cooldown = off

~$/:: ; chat pause
if on = false
{
on = true
suspend, on
}
return

~$esc::
~$enter:: ; chat unpause
suspend, off
on = false
return

$xbutton1:: reload
return

~$1::
~$2::
~$4::
~$5::
~$6::
~$7::
~$8::
~$9::
~$0::
~$-::
~$=::
hotbar = allah
return

~$3::
hotbar = chainpull
return

~$lbutton::
if cooldown = off
{
	if hotbar = chainpull
	{
	tooltip, 16, 700, 970, 1
	settimer, allahala, 1000
	cooldown = on
	count = 0
	}
}
return
	
allahala:
count++
displayed := 16-count
tooltip, %displayed%, 700, 970, 1
if displayed < 2
{
settimer, allahala, off
sleep 1000
cooldown = off
tooltip, ready, 700, 970, 1
}
return




