setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

loopcheck := 0

tooltip, PRESS P WHEN FOUND, 15, 765, 1
tooltip, ., 860, 520 ,3
tooltip, ., 860, 680 ,4
tooltip, ., 1060, 520 ,5
tooltip, ., 1060, 680 ,6

;*20 %A_ScriptDir%\Fishing\skey.png

$m::
send {a up}
send {s up}
send {d up}
reload
return

$xbutton1::
$xbutton2::
exitapp
return

$p::

returntorigin:

send {a up}
send {s up}
send {d up}

if (loopcheck > 2)
{
loopcheck := 0
}

if (loopcheck == 0)
{
send {a down}
sleep 500
returntoakey:
ImageSearch, xxx, yyy, 860, 520, 1060, 680, *TransFFFFFF
if (ErrorLevel == 0)
{
tooltip, A KEY HELD, 15, 765, 1
tooltip, , , , 2
send {lbutton down}
sleep 50
send {lbutton up}
sleep 50
goto, returntoakey
return
}
if (ErrorLevel == 1)
{
loopcheck++
tooltip, A KEY FAIL, 15, 745, 2
goto, returntorigin
}
}

if (loopcheck == 1)
{
send {s down}
sleep 500
returntoskey:
ImageSearch, xxx, yyy, 860, 520, 1060, 680, *TransFFFFFF
if (ErrorLevel == 0)
{
tooltip, S KEY HELD, 15, 765, 1
tooltip, , , , 2
send {lbutton down}
sleep 50
send {lbutton up}
sleep 50
goto, returntoskey
return
}
if (ErrorLevel == 1)
{
loopcheck++
tooltip, S KEY FAIL, 15, 745, 2
goto, returntorigin
}
}

if (loopcheck == 2)
{
send {d down}
sleep 500
returntodkey:
ImageSearch, xxx, yyy, 860, 520, 1060, 680, *TransFFFFFF
if (ErrorLevel == 0)
{
tooltip, D KEY HELD, 15, 765, 1
tooltip, , , , 2
send {lbutton down}
sleep 50
send {lbutton up}
sleep 50
goto, returntodkey
return
}
if (ErrorLevel == 1)
{
loopcheck++
tooltip, D KEY FAIL, 15, 745, 2
goto, returntorigin
}
}

goto, returntorigin

return