#SingleInstance Force
#include <Vis2>

F1::
MouseGetPos, x, y
mouseareax := 150
mouseareay := 250

picx := x-mouseareax
picy := y-mouseareax
picx2 := x+mouseareax
picy2 := y+mouseareay

capturecoords := """" picx ", " picy ", " picx2 ", " picy2 """"

pToken := Gdip_Startup()
snap := Gdip_BitmapFromScreen( picx "|" picy "|" picx2 "|" picy2 )
Gdip_SaveBitmapToFile(snap, "Shot.png")
Gdip_DisposeImage(snap)

text := OCR("Shot.png")

; Show the OCR text in a message box
MsgBox, % text