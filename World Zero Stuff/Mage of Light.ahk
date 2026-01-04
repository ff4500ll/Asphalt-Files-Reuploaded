#ifWinActive, Roblox
setbatchlines, -1
setmousedelay, -1
setkeydelay, -1

RCooldown := false
FCooldown := false
ECooldown := false
CCooldown := false
Count := 0

$xbutton2::
send {w up}
send {rbutton up}
send {lbutton up}
reload
return

$xbutton1::
send {w down}
send {rbutton down}
settimer PetAbility, 1000
StartOfLoop:
if (RCooldown == false)
	{
	Count--
	RCooldown := true
	settimer RRefresh, -3200
	send r
	send {lbutton down}
	sleep 2500
	send {lbutton up}
	}
if (FCooldown == false and CCooldown == false and Count <= 0)
	{
	Count := 2
	FCooldown := true
	settimer FRefresh, -15200
	settimer CRefresh, -3200
	send c
	sleep 400
	send f
	sleep 900
	goto StartOfLoop
	}
if (ECooldown == false and CCooldown == false and Count <= 0)
	{
	Count := 2
	ECooldown := true
	settimer ERefresh, -14200
	settimer CRefresh, -3200
	send c
	sleep 400
	send e
	sleep 800
	}
sleep 100
goto StartOfLoop
return

RRefresh:
RCooldown := false
return
FRefresh:
FCooldown := false
return
ERefresh:
ECooldown := false
return
CRefresh:
CCooldown := false
return

PetAbility:
send 1
return