#ifWinActive, Roblox
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1

$o:: reload
$m:: exitapp

$p::
CheckLocationStart:
InCave := true
tooltip %InCave%
sleep 1000
ImageSearch, , , 0, CaveY1, CaveX2, CaveY2, *10 %A_ScriptDir%\Images\Cave1.png
if (ErrorLevel == 1)
	{
	ImageSearch, , , 0, CaveY1, CaveX2, CaveY2, *10 %A_ScriptDir%\Images\Cave2.png
	if (ErrorLevel == 1)
		{
		InCave := false
		}
	}
tooltip %InCave%
return