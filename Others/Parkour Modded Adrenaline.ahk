#ifWinActive, Roblox
setkeydelay 0
adrenaline = off
c = on
on = false

*$r::
send {space}
sleep 70
send {space}
return
*$q::
send {space}
keywait q
send {space}
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

~$c::
if c = on
{
c = off
adrenaline = off
settimer, adrenaline, off
settimer, cooldown, off
settimer, offer, off
tooltip, Respawned, 303, 620, 1
settimer, ccc, 0
}
return

ccc:
settimer, ccc, off
sleep 1000
c = on
return

~*$x::
if adrenaline = off
{
adrenaline = unaccessable
adrenalinecount = 0
settimer, adrenaline, 1000
tooltip, Duration (55), 303, 620, 1
sleep 2200
adrenaline = on
return
}
if adrenaline = on
{
adrenaline = unaccessable
count22 = 0
settimer, adrenaline, off
settimer, cooldown, off
settimer, offer, 1000
tooltip, Removed (5), 303, 620, 1
}
return

offer:
count22++
display22 := 5-count22
if display22 = 0
{
adrenaline = off
settimer, offer, off
tooltip, Removed (Off), 303, 620, 1
return
}
tooltip, Removed (%display22%), 303, 620, 1
return

adrenaline:
adrenalinecount++
display := 55-adrenalinecount
if display = 0
{
send x
settimer, adrenaline, off
cooldowncount = 0
tooltip, Cooldown (5), 303, 620, 1
settimer, cooldown, 1000
return
}
tooltip, Duration (%display%), 303, 620, 1
return

cooldown:
cooldowncount++
display33 := 5-cooldowncount
if display33 = 0
{
tooltip, Ready, 303, 620, 1
settimer, cooldown, off
adrenaline = off
return
}
tooltip, Cooldown (%display33%), 303, 620, 1
return

,:: suspend