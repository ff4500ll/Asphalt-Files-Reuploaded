#SingleInstance Force
setkeydelay, 0
setmousedelay, 0
CoordMode, Tooltip, Screen
CoordMode, Pixel, Screen
CoordMode, Mouse, Screen

;=================================================================================================;

FishSlot := 4

ImageTolerance := 50
SelectFishDelay := 2000
SizeIncrement := 3

Sparkling := false
Shiny := false

Giant := false
Big := true

;=================================================================================================;

if (Sparkling != true and Sparkling != false)
	{
	msgbox, Sparkling needs to be set to true or false (check your spelling)
	exitapp
	}
if (Shiny != true and Shiny != false)
	{
	msgbox, Shiny needs to be set to true or false (check your spelling)
	exitapp
	}
if (Giant != true and Giant != false)
	{
	msgbox, Giant needs to be set to true or false (check your spelling)
	exitapp
	}
if (Big != true and Big != false)
	{
	msgbox, Big needs to be set to true or false (check your spelling)
	exitapp
	}
if (Giant == true and Big == true)
	{
	msgbox, Giant and Big cant be set to true (disable one)
	exitapp
	}
	
WinActivate, Roblox
WinGetActiveStats, Title, Width, Height, ScreenWidthLeft, ScreenHeightTop
ScreenWidthLeft := ScreenWidthLeft
ScreenWidthRight := ScreenWidthLeft+Width
ScreenHeightTop := ScreenHeightTop
ScreenHeightBottom := ScreenHeightTop+Height
tooltipSide := ScreenWidthLeft+(Width/20)
tooltipSpacing :=  ScreenHeightTop+(Height/2)
tooltip1 := tooltipSpacing-180
tooltip2 := tooltipSpacing-160
tooltip3 := tooltipSpacing-140
tooltip4 := tooltipSpacing-120
tooltip5 := tooltipSpacing-100
tooltip6 := tooltipSpacing-80
tooltip7 := tooltipSpacing-60
tooltip8 := tooltipSpacing-40
tooltip9 := tooltipSpacing-20
tooltip10 := tooltipSpacing
tooltip11 := tooltipSpacing+20
tooltip12 := tooltipSpacing+40
tooltip13 := tooltipSpacing+60
tooltip14 := tooltipSpacing+80
tooltip15 := tooltipSpacing+100
tooltip16 := tooltipSpacing+120
tooltip17 := tooltipSpacing+140
tooltip18 := tooltipSpacing+160
tooltip19 := tooltipSpacing+180
tooltip20 := tooltipSpacing+200

OGsparkling := Sparkling
OGshiny := Shiny
OGgiant := Giant
OGbig := Big
clicking := false

tooltip, Made By AsphaltCake, tooltipSide, tooltip1, 1
tooltip, Y to test | R to reload, tooltipSide, tooltip3, 3
tooltip, O to exit | P to begin, tooltipSide, tooltip4, 4

if (Sparkling == true)
	{
	tooltip, Sparkling: not detected, tooltipSide, tooltip6, 6
	}
else
	{
	tooltip, Sparkling: Disabled, tooltipSide, tooltip6, 6
	Sparkling := Done
	}

if (Shiny == true)
	{
	tooltip, Shiny: not detected, tooltipSide, tooltip7, 7
	}
else
	{
	tooltip, Shiny: Disabled, tooltipSide, tooltip7, 7
	Shiny := Done
	}
	
if (Giant == true)
	{
	tooltip, Giant: not detected, tooltipSide, tooltip8, 8
	Big := Done
	}
else if (Big == true)
	{
	tooltip, Big: not detected, tooltipSide, tooltip8, 8
	Giant := Done
	}
else
	{
	tooltip, Giant/Big: Disabled, tooltipSide, tooltip8, 8
	Giant := Done
	Big := Done
	}

tooltip, Z: increase area, tooltipSide, tooltip10, 10
tooltip, X: decrease area, tooltipSide, tooltip11, 11
tooltip, Fish Slot: %FishSlot%, tooltipSide, tooltip12, 12

count := 5
mousegetpos, xpos, ypos
Left := xpos-SizeIncrement*count
Right := xpos+SizeIncrement*count
Top := ypos-SizeIncrement*count
Bottom := ypos+SizeIncrement*count
tooltip, ., Left, Top, 17
tooltip, ., Right, Top, 18
tooltip, ., Left, Bottom, 19
tooltip, ., Right, Bottom, 20

;=================================================================================================;

m:: exitapp
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

r::
tooltip, ., Left, Top, 17
tooltip, ., Right, Top, 18
tooltip, ., Left, Bottom, 19
tooltip, ., Right, Bottom, 20
settimer, constantcheck, off
Sparkling := OGsparkling
Shiny := OGshiny
Giant := OGgiant
Big := OGbig
if (Sparkling == true)
	{
	tooltip, Sparkling: not detected, tooltipSide, tooltip6, 6
	}
else
	{
	tooltip, Sparkling: Disabled, tooltipSide, tooltip6, 6
	Sparkling := false
	}

if (Shiny == true)
	{
	tooltip, Shiny: not detected, tooltipSide, tooltip7, 7
	}
else
	{
	tooltip, Shiny: Disabled, tooltipSide, tooltip7, 7
	Shiny := false
	}
	
if (Giant == true)
	{
	tooltip, Giant: not detected, tooltipSide, tooltip8, 8
	Big := false
	}
else if (Big == true)
	{
	tooltip, Big: not detected, tooltipSide, tooltip8, 8
	Giant := false
	}
else
	{
	tooltip, Giant/Big: Disabled, tooltipSide, tooltip8, 8
	Giant := false
	Big := false
	}
return

$y::
tooltip, , , , 17
tooltip, , , , 18
tooltip, , , , 19
tooltip, , , , 20
settimer, constantcheck, 100
return

constantcheck:
if (Sparkling == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%ImageTolerance% %A_ScriptDir%\Sparkling.png
	if (ErrorLevel == 0)
		{
		tooltip, Sparkling: FOUND, tooltipSide, tooltip6, 6
		Sparkling := false
		}
	}
if (Shiny == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%ImageTolerance% %A_ScriptDir%\Shiny.png
	if (ErrorLevel == 0)
		{
		tooltip, Shiny: FOUND, tooltipSide, tooltip7, 7
		Shiny := false
		}
	}
if (Giant == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%ImageTolerance% %A_ScriptDir%\Giant.png
	if (ErrorLevel == 0)
		{
		tooltip, Giant: FOUND, tooltipSide, tooltip8, 8
		Giant := false
		}
	}
if (Big == true)
	{
	ImageSearch, , , Left, Top, Right, Bottom, *%ImageTolerance% %A_ScriptDir%\Big.png
	if (ErrorLevel == 0)
		{
		tooltip, Big: FOUND, tooltipSide, tooltip8, 8
		Big := false
		}
	}
return

$p::
tooltip, , , , 17
tooltip, , , , 18
tooltip, , , , 19
tooltip, , , , 20
clicking := true
settimer, constantcheck, 100
loop,
	{
	if (Sparkling != true and Shiny != true and Giant != true and Big != true)
		{
		send {1 down}
		sleep 10
		send {1 up}
		sleep 10
		exitapp
		}
	send {3 down}
	sleep 100
	send {3 up}
	sleep 100
	send {%FishSlot% down}
	sleep 100
	send {%FishSlot% up}
	sleep 100
	send {click}
	sleep %SelectFishDelay%
	}
return