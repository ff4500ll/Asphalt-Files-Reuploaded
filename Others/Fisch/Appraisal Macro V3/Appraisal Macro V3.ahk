#SingleInstance Force
setkeydelay, -1
setmousedelay, -1
setbatchlines, -1
SetTitleMatchMode 2

CoordMode, Tooltip, Relative
CoordMode, Pixel, Relative
CoordMode, Mouse, Relative

;=================================================================================================;

FishSlot := 4

RestartDelay := 2500
SizeIncrement := 2

SingleTriggerMode := true

Sparkling := false
Shiny := false
Hexed := true
Abyssal := true
Mythical := false
Giant := false
Big := false

SparklingTolerance := 50
ShinyTolerance := 50
HexedTolerance := 50
AbyssalTolerance := 50
MythicalTolerance := 50
GiantTolerance := 50
BigTolerance := 50

;=================================================================================================;

Calculations:
WinActivate, Roblox
if WinActive("Roblox")
	{
	WinGetActiveStats, Title, WindowWidth, WindowHeight, WindowLeft, WindowTop
	}
else
	{
	msgbox, where roblox bruh
	exitapp
	}
TooltipX := WindowWidth/20
Tooltip1 := (WindowHeight/2)-(20*9)
Tooltip2 := (WindowHeight/2)-(20*8)
Tooltip3 := (WindowHeight/2)-(20*7)
Tooltip4 := (WindowHeight/2)-(20*6)
Tooltip5 := (WindowHeight/2)-(20*5)
Tooltip6 := (WindowHeight/2)-(20*4)
Tooltip7 := (WindowHeight/2)-(20*3)
Tooltip8 := (WindowHeight/2)-(20*2)
Tooltip9 := (WindowHeight/2)-(20*1)
Tooltip10 := (WindowHeight/2)
Tooltip11 := (WindowHeight/2)+(20*1)
Tooltip12 := (WindowHeight/2)+(20*2)
Tooltip13 := (WindowHeight/2)+(20*3)
Tooltip14 := (WindowHeight/2)+(20*4)
Tooltip15 := (WindowHeight/2)+(20*5)
Tooltip16 := (WindowHeight/2)+(20*6)

tooltip, Made By AsphaltCake, TooltipX, Tooltip1, 1
tooltip, Press "P" to Start, TooltipX, Tooltip2, 2
tooltip, Press "O" to Reload, TooltipX, Tooltip3, 3
tooltip, Press "M" to Exit, TooltipX, Tooltip4, 4
tooltip, Press "Y" to Test, TooltipX, Tooltip5, 5
tooltip, "Z"=Expand|"X"=Shrink, TooltipX, Tooltip6, 6

if (Sparkling == true)
	{
	tooltip, Sparkling Enabled, TooltipX, Tooltip7, 7
	}
if (Shiny == true)
	{
	tooltip, Shiny Enabled, TooltipX, Tooltip8, 8
	}
if (Hexed == true)
	{
	tooltip, Hexed Enabled, TooltipX, Tooltip9, 9
	}
if (Abyssal == true)
	{
	tooltip, Abyssal Enabled, TooltipX, Tooltip10, 10
	}
if (Mythical == true)
	{
	tooltip, Mythical Enabled, TooltipX, Tooltip11, 11
	}
if (Giant == true)
	{
	tooltip, Giant Enabled, TooltipX, Tooltip12, 12
	}
if (Big == true)
	{
	tooltip, Big Enabled, TooltipX, Tooltip13, 13
	}
return

z::
count++
mousegetpos, xpos, ypos
Left := xpos-SizeIncrement*count
Right := xpos+SizeIncrement*count
Top := ypos-SizeIncrement*count
Bottom := ypos+SizeIncrement*count
tooltip, ., Left, Top, 17
tooltip, ., Right, Top, 18
tooltip, ., Left, Bottom, 19
tooltip, ., Right, Bottom, 20
return

x::
count--
if (count <= 0)
	{
	count := 0
	return
	}
mousegetpos, xpos, ypos
Left := xpos-SizeIncrement*count
Right := xpos+SizeIncrement*count
Top := ypos-SizeIncrement*count
Bottom := ypos+SizeIncrement*count
tooltip, ., Left, Top, 17
tooltip, ., Right, Top, 18
tooltip, ., Left, Bottom, 19
tooltip, ., Right, Bottom, 20
return

$o:: reload
$m:: exitapp
$p::
gosub Calculations
tooltip, , , , 17
tooltip, , , , 18
tooltip, , , , 19
tooltip, , , , 20

Restart:
if (Sparkling == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%SparklingTolerance% %A_ScriptDir%\Sparkling.png
	if (ErrorLevel == 0)
		{
		tooltip, Sparkling: FOUND, TooltipX, Tooltip7, 7
		FoundSparkling := true
		if (SingleTriggerMode == true)
		exitapp
		}
	else
		{
		tooltip, Sparkling: Searching, TooltipX, Tooltip7, 7
		FoundSparkling := false
		}
	}
else
	{
	tooltip, , , , 7
	FoundSparkling := true
	}
	
if (Shiny == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%ShinyTolerance% %A_ScriptDir%\Shiny.png
	if (ErrorLevel == 0)
		{
		tooltip, Shiny: FOUND, TooltipX, Tooltip8, 8
		FoundShiny := true
		if (SingleTriggerMode == true)
		exitapp
		}
	else
		{
		tooltip, Shiny: Searching, TooltipX, Tooltip8, 8
		FoundShiny := false
		}
	}
else
	{
	tooltip, , , , 8
	FoundShiny := true
	}
	
if (Hexed == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%HexedTolerance% %A_ScriptDir%\Hexed.png
	if (ErrorLevel == 0)
		{
		tooltip, Hexed: FOUND, TooltipX, Tooltip9, 9
		FoundHexed := true
		if (SingleTriggerMode == true)
		exitapp
		}
	else
		{
		tooltip, Hexed: Searching, TooltipX, Tooltip9, 9
		FoundHexed := false
		}
	}
else
	{
	tooltip, , , , 9
	FoundHexed := true
	}
	
if (Abyssal == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%AbyssalTolerance% %A_ScriptDir%\Abyssal.png
	if (ErrorLevel == 0)
		{
		tooltip, Abyssal: FOUND, TooltipX, Tooltip10, 10
		FoundAbyssal := true
		if (SingleTriggerMode == true)
		exitapp
		}
	else
		{
		tooltip, Abyssal: Searching, TooltipX, Tooltip10, 10
		FoundAbyssal := false
		}
	}
else
	{
	tooltip, , , , 10
	FoundAbyssal := true
	}
	
if (Mythical == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%MythicalTolerance% %A_ScriptDir%\Mythical.png
	if (ErrorLevel == 0)
		{
		tooltip, Mythical: FOUND, TooltipX, Tooltip11, 11
		FoundMythical := true
		if (SingleTriggerMode == true)
		exitapp
		}
	else
		{
		tooltip, Mythical: Searching, TooltipX, Tooltip11, 11
		FoundMythical := false
		}
	}
else
	{
	tooltip, , , , 11
	FoundMythical := true
	}
	
if (Giant == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%GiantTolerance% %A_ScriptDir%\Giant.png
	if (ErrorLevel == 0)
		{
		tooltip, Giant: FOUND, TooltipX, Tooltip12, 12
		FoundGiant := true
		if (SingleTriggerMode == true)
		exitapp
		}
	else
		{
		tooltip, Giant: Searching, TooltipX, Tooltip12, 12
		FoundGiant := false
		}
	}
else
	{
	tooltip, , , , 12
	FoundGiant := true
	}
	
if (Big == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%BigTolerance% %A_ScriptDir%\Big.png
	if (ErrorLevel == 0)
		{
		tooltip, Big: FOUND, TooltipX, Tooltip13, 13
		FoundBig := true
		if (SingleTriggerMode == true)
		exitapp
		}
	else
		{
		tooltip, Big: Searching, TooltipX, Tooltip13, 13
		FoundBig := false
		}
	}
else
	{
	tooltip, , , , 13
	FoundBig := true
	}

if (FoundSparkling == true and FoundShiny == true and FoundHexed == true and FoundAbyssal == true and FoundMythical == true and FoundGiant == true and FoundBig == true)
exitapp

send {3}
sleep 100
send {%FishSlot%}
sleep 100
send {click}
sleep %RestartDelay%
goto Restart

$y::
gosub Calculations
tooltip, , , , 17
tooltip, , , , 18
tooltip, , , , 19
tooltip, , , , 20

Restart2:
if (Sparkling == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%SparklingTolerance% %A_ScriptDir%\Sparkling.png
	if (ErrorLevel == 0)
		{
		tooltip, Sparkling: FOUND, TooltipX, Tooltip7, 7
		FoundSparkling := true
		}
	else
		{
		tooltip, Sparkling: Searching, TooltipX, Tooltip7, 7
		FoundSparkling := false
		}
	}
else
	{
	tooltip, , , , 7
	FoundSparkling := true
	}
	
if (Shiny == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%ShinyTolerance% %A_ScriptDir%\Shiny.png
	if (ErrorLevel == 0)
		{
		tooltip, Shiny: FOUND, TooltipX, Tooltip8, 8
		FoundShiny := true
		}
	else
		{
		tooltip, Shiny: Searching, TooltipX, Tooltip8, 8
		FoundShiny := false
		}
	}
else
	{
	tooltip, , , , 8
	FoundShiny := true
	}
	
if (Hexed == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%HexedTolerance% %A_ScriptDir%\Hexed.png
	if (ErrorLevel == 0)
		{
		tooltip, Hexed: FOUND, TooltipX, Tooltip9, 9
		FoundHexed := true
		}
	else
		{
		tooltip, Hexed: Searching, TooltipX, Tooltip9, 9
		FoundHexed := false
		}
	}
else
	{
	tooltip, , , , 9
	FoundHexed := true
	}
	
if (Abyssal == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%AbyssalTolerance% %A_ScriptDir%\Abyssal.png
	if (ErrorLevel == 0)
		{
		tooltip, Abyssal: FOUND, TooltipX, Tooltip10, 10
		FoundAbyssal := true
		}
	else
		{
		tooltip, Abyssal: Searching, TooltipX, Tooltip10, 10
		FoundAbyssal := false
		}
	}
else
	{
	tooltip, , , , 10
	FoundAbyssal := true
	}
	
if (Mythical == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%MythicalTolerance% %A_ScriptDir%\Mythical.png
	if (ErrorLevel == 0)
		{
		tooltip, Mythical: FOUND, TooltipX, Tooltip11, 11
		FoundMythical := true
		}
	else
		{
		tooltip, Mythical: Searching, TooltipX, Tooltip11, 11
		FoundMythical := false
		}
	}
else
	{
	tooltip, , , , 11
	FoundMythical := true
	}
	
if (Giant == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%GiantTolerance% %A_ScriptDir%\Giant.png
	if (ErrorLevel == 0)
		{
		tooltip, Giant: FOUND, TooltipX, Tooltip12, 12
		FoundGiant := true
		}
	else
		{
		tooltip, Giant: Searching, TooltipX, Tooltip12, 12
		FoundGiant := false
		}
	}
else
	{
	tooltip, , , , 12
	FoundGiant := true
	}
	
if (Big == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%BigTolerance% %A_ScriptDir%\Big.png
	if (ErrorLevel == 0)
		{
		tooltip, Big: FOUND, TooltipX, Tooltip13, 13
		FoundBig := true
		}
	else
		{
		tooltip, Big: Searching, TooltipX, Tooltip13, 13
		FoundBig := false
		}
	}
else
	{
	tooltip, , , , 13
	FoundBig := true
	}
	
sleep %RestartDelay%
goto Restart2