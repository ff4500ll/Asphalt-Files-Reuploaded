setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

fishingrodkeybind = 2
keyswapdelay = 100
interact = y
tolerance = 100
clickdelay = 100 ;in miliseconds

clicking = false
fishingstate = false
holdingrod = false
mathismathing = (clickdelay/2)

aleft = 1207
aright = 1225
atop = 748
abottom = 766

sleft = 1273
sright = 1288
stop = 810
sbottom = 833

dleft = 1336
dright = 1355
dtop = 747
dbottom = 766

cleft = 1100
cright = 1456
ctop = 480
cbottom = 1035

$m:: reload
$':: exitapp

$l::
loop,
{
MouseGetPos, xpos, ypos 
tooltip, X:%xpos% Y:%ypos%, 200, 200
sleep 100
}
return

$p::
returntostart:

send {%fishingrodkeybind% down}
sleep 10
send {%fishingrodkeybind% up}
sleep 10

send {lbutton down}
sleep 10
send {lbutton up}
sleep 10

fishingstate = false
faillooppoint:

ImageSearch, xxx, yyy, %aleft%, %atop%, %aright%, %abottom%, *%tolerance% %A_ScriptDir%\fishing\white.png
if (ErrorLevel = 0)
{

if fishingstate = false
{
fishingstate = true
}

tooltip, a held down, 200, 200
send {s up}
sleep 10
send {d up}
sleep 10
send {a down}
sleep 10

if clicking = false
{
clicking = true
settimer, click, %clickdelay%
}
sleep %keyswapdelay%
goto, faillooppoint

}
if (ErrorLevel = 1)
{

ImageSearch, xxx, yyy, %sleft%, %stop%, %sright%, %sbottom%, *%tolerance% %A_ScriptDir%\fishing\white.png
if (ErrorLevel = 0)
{

if fishingstate = false
{
fishingstate = true
}

tooltip, s held down, 200, 200
send {a up}
sleep 10
send {d up}
sleep 10
send {s down}
sleep 10

if clicking = false
{
clicking = true
settimer, click, %clickdelay%
}
sleep %keyswapdelay%
goto, faillooppoint

}
if (ErrorLevel = 1)
{

ImageSearch, xxx, yyy, %dleft%, %dtop%, %dright%, %dbottom%, *%tolerance% %A_ScriptDir%\fishing\white.png
if (ErrorLevel = 0)
{

if fishingstate = false
{
fishingstate = true
}

tooltip, d held down, 200, 200
send {a up}
sleep 10
send {s up}
sleep 10
send {d down}
sleep 10

if clicking = false
{
clicking = true
settimer, click, %clickdelay%
}
sleep %keyswapdelay%
goto, faillooppoint

}
if (ErrorLevel = 1)
{
tooltip, nothing detected, 200, 200
send {a up}
sleep 10
send {s up}
sleep 10
send {d up}
sleep 10
clicking = false
settimer, click, off

if fishingstate = false
{
goto, faillooppoint
}

sleep 1000

}
}
}

send {%fishingrodkeybind% down}
sleep 10
send {%fishingrodkeybind% up}
sleep 500

send {s down}
sleep 100
send {q down}
sleep 10
send {s up}
send {q up}

send {%interact% down}
sleep 100
send {%interact% up}
sleep 500

ImageSearch, xxx, yyy, %cleft%, %ctop%, %cright%, %cbottom%, *%tolerance% %A_ScriptDir%\fishing\exit.png
if (ErrorLevel = 0)
{
send {shift down}
sleep 100
send {shift up}
sleep 3000
ImageSearch, xxx, yyy, %cleft%, %ctop%, %cright%, %cbottom%, *%tolerance% %A_ScriptDir%\fishing\loot.png
click %xxx% %yyy%
sleep 500

send {shift down}
sleep 100
send {shift up}
sleep 100
send {s down}
sleep 100
send {q down}
sleep 10
send {s up}
send {q up}
}

goto, returntostart
return

click:
send {lbutton down}
sleep %mathismathing%
send {lbutton up}
return









