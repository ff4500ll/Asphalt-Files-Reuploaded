local ReplicatedStorage = game:GetService("ReplicatedStorage");
local UserInputService = game:GetService("UserInputService");
local TweenService = game:GetService("TweenService");
local RunService = game:GetService("RunService");
local LocalPlayer = game:GetService("Players").LocalPlayer;

local reelProgressBar = 20;
local reelDirection = -1;
local reelSpeed = 0;
local lastInputTime = tick();
local bounceFactor = 0.5;
local lastBounceTime = tick();
local lastReelTime = tick();
local lastUpdateTime = tick();
local progressDecayRate = math.clamp(0 / 100, 0.2, 9999);

local playerBar = script.Parent:WaitForChild("playerbar");
local fishBar = script.Parent:WaitForChild("fish");
local progressBar = script.Parent:WaitForChild("progress"):WaitForChild("bar");
local parentGui = script.Parent.Parent;

local barColorTween = TweenService:Create(progressBar, TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.Out, 0, true), {
	BackgroundColor3 = Color3.new(1, 0, 0)
});

local function isStarterCatchEligible(fish)
	if fish then
		return fish:GetAttribute("AB_StarterCatch") == true;
	else
		return false;
	end;
end;

local function createAndPlayTween(target, tweenInfo, properties)
	local tween = TweenService:Create(target, tweenInfo, properties);
	tween.Completed:Once(function()
		tween:Destroy();
	end);
	tween:Play();
	return tween;
end;

local function roundToTenth(value)
	return math.round(value * 10) / 10;
end;

local progressSpeed = 0.01;

-- IMPORTANT
-- base color is 255,255,255, but the progress bar color for fish with debuffs is 159,159,159

if progressSpeed > 1 then
	script.Parent:WaitForChild("progress_speed").Visible = true;
	script.Parent.progress_speed.Text = "+" .. tostring(math.round(math.round(progressSpeed * 100 - 100) * 10) / 10) .. "% Progress Speed";
elseif progressSpeed < 1 then
	script.Parent:WaitForChild("progress_speed").Visible = true;
	script.Parent.progress_speed.Text = "-" .. tostring((math.round(100 - progressSpeed * 100))) .. "% Progress Speed";
	script.Parent.progress.bar.BackgroundColor3 = Color3.fromRGB(159, 159, 159);
else
	script.Parent:WaitForChild("progress_speed").Visible = false;
end;

local playerBarScale = 1;
playerBar.Size = UDim2.new((playerBar.Size.X.Scale) * playerBarScale, 0, playerBar.Size.Y.Scale, 0);
fishBar:WaitForChild("sparkles").Enabled = script.fish:GetAttribute("Special");

-- IMPORTANT
-- Updates the colors basically making a simulation

local function updateColors()
	local colorSequence = ColorSequence.new({
		ColorSequenceKeypoint.new(0, Color3.new(0.388235, 0.164706, 0.164706):Lerp(Color3.new(0.34902, 0.494118, 0.34902), reelProgressBar / 100)), 
		ColorSequenceKeypoint.new(0.1, Color3.new(0.388235, 0.164706, 0.164706):Lerp(Color3.new(0.34902, 0.494118, 0.34902), reelProgressBar / 100)), 
		ColorSequenceKeypoint.new(0.2, Color3.new(1, 1, 1)), 
		ColorSequenceKeypoint.new(0.8, Color3.new(1, 1, 1)), 
		ColorSequenceKeypoint.new(0.9, Color3.new(0.388235, 0.164706, 0.1647062):Lerp(Color3.new(0.34902, 0.494118, 0.34902), reelProgressBar / 100)), 
		ColorSequenceKeypoint.new(1, Color3.new(0.388235, 0.164706, 0.164706):Lerp(Color3.new(0.34902, 0.494118, 0.34902), reelProgressBar / 100))
	});
	script.Parent.stroke.UIGradient.Color = colorSequence;
	script.Parent.licon.ImageColor3 = Color3.new(0.388235, 0.164706, 0.164706):Lerp(Color3.new(0.34902, 0.494118, 0.34902), reelProgressBar / 100);
	script.Parent.ricon.ImageColor3 = Color3.new(0.388235, 0.164706, 0.164706):Lerp(Color3.new(0.34902, 0.494118, 0.34902), reelProgressBar / 100);
	progressBar.Size = UDim2.new(math.clamp(reelProgressBar / 100, 0, 1), 0, 1, 0);
end;

local isReeling = true;
local reelMultiplier = 1;
local isReelActive = false;
local currentTween = nil;

-- REALLY IMPORTANT
UserInputService.InputBegan:Connect(function(input)
	if input.UserInputType == Enum.UserInputType.MouseButton1 or input.KeyCode == Enum.KeyCode.Space or input.UserInputType == Enum.UserInputType.Touch or input.KeyCode == Enum.KeyCode.ButtonA then
		reelDirection = 1;
		lastInputTime = tick();
		playerBar:WaitForChild("xboxcontrol").ImageColor3 = Color3.fromRGB(88, 109, 129);
		script.Parent.pc.ImageColor3 = Color3.fromRGB(88, 109, 129);
		script.Parent:WaitForChild("mobile").ImageColor3 = Color3.fromRGB(88, 109, 129);

		-- might be slash effect
		if (reelProgressBar > 0.1 and reelProgressBar < 100 or tick() - lastReelTime <= 5) and isReelActive == true then
			if currentTween then
				currentTween:Cancel();
				currentTween = nil;
			end;
			local currentCamera = workspace.CurrentCamera;
			local tweenInfo = TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out);
			local tweenProperties = {
				FieldOfView = 55
			};
			local tween = TweenService:Create(currentCamera, tweenInfo, tweenProperties);
			tween.Completed:Once(function()
				tween:Destroy();
			end);
			tween:Play();
			currentTween = tween;
			if isReeling then
				isReeling.Stop();
				isReeling = nil;
			end;
		end;

		-- REALLY REALLY IMPORTANT

		if reelDirection < 0 then
			if playerBar.left.Visible == false then
				local handle = playerBar.Rod.Handle;
				local tweenInfo = TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out);

				local tweenProperties = {
					Position = UDim2.new(0.48, 0, 0.261, 0), 
					Rotation = -90
				};

				local tween = TweenService:Create(handle, tweenInfo, tweenProperties);
				tween.Completed:Once(function()
					tween:Destroy();
				end);
				tween:Play();
			end;
			playerBar.left.Visible = true;
			playerBar.right.Visible = false;
			return;
		else
			if playerBar.right.Visible == false then
				local handle = playerBar.Rod.Handle;
				local tweenInfo = TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out);
				local tweenProperties = {
					Position = UDim2.new(0.529, 0, 0.243, 0), 
					Rotation = 90
				};
				local tween = TweenService:Create(handle, tweenInfo, tweenProperties);
				tween.Completed:Once(function()
					tween:Destroy();
				end);
				tween:Play();
			end;
			playerBar.left.Visible = false;
			playerBar.right.Visible = true;

		end;
	end;
end);

UserInputService.InputEnded:Connect(function(input)
	if input.UserInputType == Enum.UserInputType.MouseButton1 or input.KeyCode == Enum.KeyCode.Space or input.UserInputType == Enum.UserInputType.Touch or input.KeyCode == Enum.KeyCode.ButtonA then
		reelDirection = -1;
		lastInputTime = tick();
		playerBar:WaitForChild("xboxcontrol").ImageColor3 = Color3.fromRGB(239, 239, 239);
		script.Parent.pc.ImageColor3 = Color3.fromRGB(239, 239, 239);
		script.Parent:WaitForChild("mobile").ImageColor3 = Color3.fromRGB(239, 239, 239);
		if isReeling then
			isReeling.Stop();
			isReeling = nil;
		end;
		if (reelProgressBar > 0.1 and reelProgressBar < 100 or tick() - lastReelTime <= 5) and isReelActive == true then
			if currentTween then
				currentTween:Cancel();
				currentTween = nil;
			end;
			local currentCamera = workspace.CurrentCamera;
			local tweenInfo = TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.Out);
			local tweenProperties = {
				FieldOfView = 56
			};
			local tween = TweenService:Create(currentCamera, tweenInfo, tweenProperties);
			tween.Completed:Once(function()
				tween:Destroy();
			end);
			tween:Play();
			currentTween = tween;
		end;

		-- REALLY IMPORTANT
		if reelDirection < 0 then
			if playerBar.left.Visible == false then
				local handle = playerBar.Rod.Handle;
				local tweenInfo = TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out);
				local tweenProperties = {
					Position = UDim2.new(0.48, 0, 0.261, 0), 
					Rotation = -90
				};
				local tween = TweenService:Create(handle, tweenInfo, tweenProperties);
				tween.Completed:Once(function()
					tween:Destroy();
				end);
				tween:Play();
			end;
			playerBar.left.Visible = true;
			playerBar.right.Visible = false;
			return;
		else
			if playerBar.right.Visible == false then
				local handle = playerBar.Rod.Handle;
				local tweenInfo = TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out);
				local tweenProperties = {
					Position = UDim2.new(0.529, 0, 0.243, 0), 
					Rotation = 90
				};
				local tween = TweenService:Create(handle, tweenInfo, tweenProperties);
				tween.Completed:Once(function()
					tween:Destroy();
				end);
				tween:Play();
			end;
			playerBar.left.Visible = false;
			playerBar.right.Visible = true;
		end;
	end;
end);

if script:FindFirstAncestorWhichIsA("PlayerGui"):FindFirstChild("hud") then
	script:FindFirstAncestorWhichIsA("PlayerGui"):FindFirstChild("hud").Enabled = false;
end;
updateColors();

progressBar.Size = UDim2.new(0, 0, 1, 0);
progressBar.Transparency = 1;
playerBar.Transparency = 1;
fishBar.Position = UDim2.new(0.5, 0, 0.5, 0);
local playerBarTween = TweenService:Create(playerBar, TweenInfo.new(1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
	Transparency = 0
});

local playerBarTweenCopy = playerBarTween;
playerBarTween.Completed:Once(function()
	playerBarTweenCopy:Destroy();
end);
playerBarTween:Play();

playerBarTween = TweenService:Create(progressBar, TweenInfo.new(1.9, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
	Size = UDim2.new(math.clamp(reelProgressBar / 100, 0, 1), 0, 1, 0), 
	Transparency = 0
});

local playerBarTweenCopy2 = playerBarTween;
playerBarTween.Completed:Once(function()
	playerBarTweenCopy2:Destroy();
end);

playerBarTween:Play();
local rodEffects = {
	["Trident Rod"] = fishBar.TridentSlash, 
	["Leviathan's Fang Rod"] = fishBar.LeviathansFangSlash, 
	["No-Life Rod"] = fishBar.TridentSlashEvil, 
	["Abyssal Spinecaster"] = fishBar.TridentSlashSpinecaster, 
	["Tetra Rod"] = fishBar.TridentSlashTetra, 
	["Ultratech Rod"] = fishBar.TridentSlashSpinecaster, 
	["Katana Rod"] = fishBar.TridentSlashKatana, 
	["Pen Rod"] = fishBar.TridentSlashPen, 
	["Fabulous Rod"] = fishBar.TridentSlashFabulous, 
	["Mila's Wand Of Magic"] = fishBar.TridentSlashMila
};

local rodGradients = {
	["Leviathan's Fang Rod"] = script.LeviathansFangGradient, 
	["Trident Rod"] = script.TridentGradient, 
	["No-Life Rod"] = script["No-LifeGradient"], 
	["Abyssal Spinecaster"] = script.SpinecasterGradient, 
	["Tetra Rod"] = script["No-LifeGradient"], 
	["Ultratech Rod"] = script.UltratechGradient, 
	["Katana Rod"] = script.KatanaGradient, 
	["Pen Rod"] = script.PenGradient, 
	["Fabulous Rod"] = script.FabulousGradient, 
	["Mila's Wand Of Magic"] = script.MilaGradient
};

local function playRodEffect(isSpecial)
	if LocalPlayer.Character then
		local playbackSpeed = Random.new():NextNumber(0.95, 1.1);
		if isSpecial then
			if LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab").PlaybackSpeed = playbackSpeed;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab"):Play();
			end;
		elseif script.rod.Value.Name == "Abyssal Spinecaster" or script.rod.Value.Name == "Ultratech Rod" then
			if LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabspinecaster") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabspinecaster").PlaybackSpeed = playbackSpeed * 0.85;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabspinecaster"):Play();
			end;
			if LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabspinecaster2") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabspinecaster2").PlaybackSpeed = playbackSpeed;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabspinecaster2"):Play();
			end;
		elseif script.rod.Value.Name == "Tetra Rod" then
			if LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabtetra") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabtetra").PlaybackSpeed = playbackSpeed;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabtetra"):Play();
			end;
		elseif script.rod.Value.Name == "Pen Rod" then
			if LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabpen") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabpen").PlaybackSpeed = playbackSpeed;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabpen"):Play();
			end;
		elseif script.rod.Value.Name == "Fabulous Rod" then
			if LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabgreen") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabgreen").PlaybackSpeed = playbackSpeed;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystabgreen"):Play();
			end;
		elseif script.rod.Value.Name == "Mila's Wand Of Magic" then
			if LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab").PlaybackSpeed = playbackSpeed;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab"):Play();
			end;
		elseif LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab") then
			LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab").PlaybackSpeed = playbackSpeed;
			LocalPlayer.Character.HumanoidRootPart:FindFirstChild("stabbystab"):Play();
		end;
	end;
	local effect = rodEffects[script.rod.Value.Name] ~= nil and rodEffects[script.rod.Value.Name]:Clone() or fishBar.TridentSlash:Clone();
	effect.Size = UDim2.fromScale(0, 0);
	effect.ImageTransparency = 0;
	effect.Parent = fishBar;
	local effectColor = Color3.fromRGB(255, 255, 255);

	if isSpecial then
		effect.UIGradient.Color = ColorSequence.new({
			ColorSequenceKeypoint.new(0, Color3.fromRGB(182, 182, 182)), 
			ColorSequenceKeypoint.new(0.5, Color3.fromRGB(255, 255, 255)), 
			ColorSequenceKeypoint.new(1, Color3.fromRGB(182, 182, 182))
		});
		effect.ImageColor3 = effectColor;
	end;

	local tweenInfo = TweenInfo.new(0.4, Enum.EasingStyle.Cubic, Enum.EasingDirection.Out);
	local tweenProperties = {
		Size = UDim2.fromScale(10.188, 4.5)
	};

	local tween = TweenService:Create(effect, tweenInfo, tweenProperties);
	tween.Completed:Once(function()
		tween:Destroy();
	end);

	tween:Play();
	tweenProperties = ColorSequence.new({
		ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 255, 255)), 
		ColorSequenceKeypoint.new(0.3, effectColor), 
		ColorSequenceKeypoint.new(0.5, effectColor), 
		ColorSequenceKeypoint.new(0.8, effectColor), 
		ColorSequenceKeypoint.new(1, Color3.fromRGB(255, 255, 255))
	});
	task.defer(function()
		local tweenInfo = TweenInfo.new(2, Enum.EasingStyle.Circular, Enum.EasingDirection.Out);
		local tweenProperties = {
			Offset = Vector2.new(1, 0)
		};
		local tween = TweenService:Create(script.Parent.progress.bar.UIGradient, tweenInfo, tweenProperties);
		local offset = Vector2.new(-1, 0);
		if isSpecial then
			script.Parent.progress.bar.UIGradient.Color = tweenProperties;
		else
			script.Parent.progress.bar.UIGradient.Color = rodGradients[script.rod.Value.Name] ~= nil and rodGradients[script.rod.Value.Name].Color or script.TridentGradient.Color;
		end;
		script.Parent.progress.bar.UIGradient.Offset = offset;
		tween:Play();
		tween.Completed:Wait();
		script.Parent.progress.bar.UIGradient.Offset = offset;
	end);

	task.delay(tweenInfo.Time, function()
		local tweenInfo = TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut);
		local tweenProperties = {
			Size = UDim2.fromScale(7, 4.75), 
			ImageTransparency = 1
		};
		local tween = TweenService:Create(effect, tweenInfo, tweenProperties);
		tween.Completed:Once(function()
			tween:Destroy();
		end);
		tween:Play();
	end);
end;

local function lerp(a, b, t)
	return a + (b - a) * t;
end;

local function impact(target, startPosition, duration, interval, shouldRotate, decayFactor)
	local intensity = 0.8;
	for _ = 0, duration, interval do
		target.Position = startPosition:Lerp(startPosition + UDim2.new(Random.new():NextNumber(-0.05, 0.05), 0, Random.new():NextNumber(-0.08, 0.08), 0), intensity);
		if shouldRotate then
			target.Rotation = 0 + (Random.new():NextNumber(-8, 8) - 0) * intensity;
		end;
		intensity = intensity * (decayFactor or 0.9);
		task.wait(interval);
	end;
	target.Position = startPosition;
	target.Rotation = shouldRotate and 0 or target.Rotation;
end;

local function ftueProgressBoost()
	print("entering ftue tutorial mode");
	reelProgressBar = 50;
	reelMultiplier = 0.4;
end;

local function voyagerLaser(amount)
	task.spawn(impact, script.Parent, script.Parent.Position, 3, 0.025, true, 0.97);
	for _ = 1, 40 do
		local newProgress = reelProgressBar + amount;
		if newProgress > 60 then
			reelProgressBar = 60;
			return;
		else
			reelProgressBar = newProgress;
			task.wait(0.075);
		end;
	end;
end;

local function mikuLaser(amount)
	task.spawn(impact, script.Parent, script.Parent.Position, 3, 0.025, true, 0.97);
	for _ = 1, 40 do
		local newProgress = reelProgressBar + amount;
		if newProgress > 99 then
			reelProgressBar = 99;
			return;
		else
			reelProgressBar = newProgress;
			task.wait(0.075);
		end;
	end;
end;

if LocalPlayer.Character and LocalPlayer.Character.HumanoidRootPart:FindFirstChild("reeling") then
	LocalPlayer.Character.HumanoidRootPart:FindFirstChild("reeling").Volume = 0.08;
end;
local cameraTween = TweenService:Create(workspace.CurrentCamera, TweenInfo.new(0.6, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
	FieldOfView = 56
});
local cameraTweenCopy = cameraTween;
cameraTween.Completed:Once(function()
	cameraTweenCopy:Destroy();
end);
cameraTween:Play();

if reelDirection < 0 then
	if playerBar.left.Visible == false then
		cameraTween = TweenService:Create(playerBar.Rod.Handle, TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			Position = UDim2.new(0.48, 0, 0.261, 0), 
			Rotation = -90
		});
		local cameraTweenCopy2 = cameraTween;
		cameraTween.Completed:Once(function()
			cameraTweenCopy2:Destroy();
		end);
		cameraTween:Play();
	end;
	playerBar.left.Visible = true;
	playerBar.right.Visible = false;
else
	if playerBar.right.Visible == false then
		cameraTween = TweenService:Create(playerBar.Rod.Handle, TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			Position = UDim2.new(0.529, 0, 0.243, 0), 
			Rotation = 90
		});
		local cameraTweenCopy3 = cameraTween;
		cameraTween.Completed:Once(function()
			cameraTweenCopy3:Destroy();
		end);
		cameraTween:Play();
	end;
	playerBar.left.Visible = false;
	playerBar.right.Visible = true;
end;

local function updateInputUI()
	if UserInputService:GetLastInputType() == Enum.UserInputType.Gamepad1 then
		script.Parent.playerbar:WaitForChild("xboxcontrol").Visible = true;
		script.Parent.pc.Visible = false;
		script.Parent.mobile.Visible = false;
		return;
	elseif UserInputService:GetLastInputType() == Enum.UserInputType.Keyboard or UserInputService:GetLastInputType() == Enum.UserInputType.MouseButton1 then
		script.Parent.pc.Visible = true;
		script.Parent.playerbar:WaitForChild("xboxcontrol").Visible = false;
		script.Parent.mobile.Visible = false;
		return;
	elseif UserInputService:GetLastInputType() == Enum.UserInputType.Touch then
		script.Parent.mobile.Visible = true;
		script.Parent.pc.Visible = false;
		script.Parent.playerbar:WaitForChild("xboxcontrol").Visible = false;
		return;
	else
		script.Parent.mobile.Visible = false;
		script.Parent.pc.Visible = true;
		script.Parent.playerbar:WaitForChild("xboxcontrol").Visible = false;
		return;
	end;
end;

UserInputService.LastInputTypeChanged:Connect(function()
	updateInputUI();
end);

updateInputUI();
task.wait(0.8);
updateInputUI();

isReelActive = true;
script.Parent.Visible = true;
parentGui.Enabled = true;
task.wait(1.2);

local reelConnection = nil;
lastReelTime = tick();
local elapsedTime = 0;
cameraTween = 0;
local isReelComplete = false;
local isReelStarted = true;
local reelMultiplier = 1;
if workspace:GetAttribute("PoseidonWrathActive") and script.zone.Value == "Poseidon Pool" then
	reelMultiplier = 2;
end;

local LocalPlayer = game:GetService("Players").LocalPlayer;

reelSpeed = 0;

reelConnection = RunService.PostSimulation:Connect(function(deltaTime)
	local elapsedTime = os.clock() - elapsedTime;
	elapsedTime = os.clock();

	if reelProgressBar > 0.1 and reelProgressBar < 100 then

		reelSpeed = math.clamp(reelSpeed + reelDirection * 1 * (tick() - lastInputTime) * (deltaTime * 60), -14, 14);
		
		local minPosition = 0 + playerBar.Size.X.Scale / 2;
		local maxPosition = 1 - playerBar.Size.X.Scale / 2 + 0.001;
		if maxPosition < minPosition then
			maxPosition = minPosition;
		end;
		playerBar.Position = UDim2.new(math.clamp(playerBar.Position.X.Scale + reelSpeed * 0.001 * (deltaTime * 60), minPosition, maxPosition), 0, 0.5, 0);
		if tick() - lastBounceTime >= 0.5 then
			bounceFactor = 0.5;
		end;
		
		if playerBar.Position.X.Scale <= playerBar.Size.X.Scale / 2 or playerBar.Position.X.Scale >= 0.999999 - playerBar.Size.X.Scale / 2 then
			reelSpeed = reelSpeed * -bounceFactor;
			bounceFactor = bounceFactor / 2;
			lastBounceTime = tick();
		end;
		
		-- if fish is in area
		if fishBar.Position.X.Scale > playerBar.Position.X.Scale - playerBar.Size.X.Scale / 2 - fishBar.Size.X.Scale / 2 and fishBar.Position.X.Scale < playerBar.Position.X.Scale + playerBar.Size.X.Scale / 2 + fishBar.Size.X.Scale / 2 then
			playerBar.BackgroundTransparency = 0;
			playerBar.BackgroundColor3 = Color3.fromRGB(255, 255, 255);
			local progressIncrease = 0.2 * (1);
			reelProgressBar = math.clamp(reelProgressBar + progressIncrease * progressSpeed * (deltaTime * 60), -1, 100);
			if LocalPlayer.Character and LocalPlayer.Character.HumanoidRootPart:FindFirstChild("reeling") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("reeling").Volume = 0.15;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("reeling").PlaybackSpeed = math.clamp(reelProgressBar / 100, 0.8, 1.2) + 0.1;
			end;
		else
			playerBar.Transparency = 0.2;
			playerBar.BackgroundColor3 = Color3.new(0.388235, 0.164706, 0.164706):Lerp(Color3.new(0.34902, 0.494118, 0.34902), reelProgressBar / 100);
			reelProgressBar = math.clamp(reelProgressBar - (0.2 * (deltaTime * 60) + (tick() - lastReelTime) * (progressDecayRate * 0.0017)) * reelMultiplier, -1, 100);
			if LocalPlayer.Character and LocalPlayer.Character.HumanoidRootPart:FindFirstChild("reeling") then
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("reeling").Volume = 0.08;
				LocalPlayer.Character.HumanoidRootPart:FindFirstChild("reeling").PlaybackSpeed = math.clamp(reelProgressBar / 100, 0.8, 1.2) + 0.1;
			end;
			isReeling = false;
		end;
		updateColors();
		progressBar.Size = UDim2.new(math.clamp(reelProgressBar / 100, 0, 1), 0, 1, 0);
		
		if not (tick() - lastReelTime > math.random(progressDecayRate * 20, progressDecayRate * 51) / (reelMultiplier * 10)) then
			reelConnection:Disconnect();
			if currentTween then
				currentTween:Cancel();
				currentTween = nil;
			end;
			if script:FindFirstAncestorWhichIsA("PlayerGui"):FindFirstChild("hud") then
				script:FindFirstAncestorWhichIsA("PlayerGui"):FindFirstChild("hud").Enabled = true;
			end;
			if reelProgressBar >= 100 then
				local currentCamera = workspace.CurrentCamera;
				local tweenInfo = TweenInfo.new(3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out);
				local tweenProperties = {
					FieldOfView = 70
				};
				local tween = TweenService:Create(currentCamera, tweenInfo, tweenProperties);
				tween.Completed:Once(function()
					tween:Destroy();
				end);
				tween:Play();
			else
				local currentCamera = workspace.CurrentCamera;
				local tweenInfo = TweenInfo.new(0.6, Enum.EasingStyle.Back, Enum.EasingDirection.Out, 0, false, 1);
				local tweenProperties = {
					FieldOfView = 70
				};
				local tween = TweenService:Create(currentCamera, tweenInfo, tweenProperties);
				tween.Completed:Once(function()
					tween:Destroy();
				end);
				tween:Play();
			end;
		end
	end
end)

local LocalPlayerCharacter = LocalPlayer.Character or LocalPlayer.CharacterAdded:Wait();