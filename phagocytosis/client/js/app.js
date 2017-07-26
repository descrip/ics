//HTML element of the text box where the username is entered.
var playerNameInput = document.getElementById('playerNameInput');
//Image of a virus (green spiky thing).
var virusImage = new Image();
virusImage.src = "./res/virus.png";

//Checks if the current value in the text box contains a valid name.
var validPlayerName = function(){
	//Returns true of the length of the name is less than 15 chars.
	if (playerNameInput.value.length < 15)
		return true;
	return false;
}

//Main function, where the running of the game takes place.
function runGame(){
	// requestAnimationFrame polyfill so that it will work on all browsers
	// Erik Möller, Paul Irish, Tino Zijdel
	// http://paulirish.com/2011/requestanimationframe-for-smart-animating/
	// http://my.opera.com/emoller/blog/2011/12/20/requestanimationframe-for-smart-er-animating
	(function() {
		var lastTime = 0;
		var vendors = ['ms', 'moz', 'webkit', 'o'];
		for(var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
			window.requestAnimationFrame = window[vendors[x]+'RequestAnimationFrame'];
			window.cancelAnimationFrame = window[vendors[x]+'CancelAnimationFrame']
									|| window[vendors[x]+'CancelRequestAnimationFrame'];
		}
	
		if (!window.requestAnimationFrame)
			window.requestAnimationFrame = function(callback, element) {
				var currTime = new Date().getTime();
				var timeToCall = Math.max(0, 16 - (currTime - lastTime));
				var id = window.setTimeout(function() { callback(currTime + timeToCall); },
				timeToCall);
				lastTime = currTime + timeToCall;
				return id;
			};
	
		if (!window.cancelAnimationFrame)
			window.cancelAnimationFrame = function(id) {
				clearTimeout(id);
			};
	}());	
	
	//Pretend these are static variables.
	//Width of one tile.
	var TILEWIDTH = 30;
	//A constant used in speed calculations.
	var SPEEDCONST = 40;
	//The radius of a food object.
	var FOODRADIUS = 10;
	//Widths for borders in cells, food, and text.
	var CELLBORDERWIDTH = 6;
	var FOODBORDERWIDTH = 2;
	var TEXTBORDERWIDTH = 2;
	//The initial mass for each cell.
	var STARTMASS = 10;
	//Minimum font size when drawing names.
	var MINFONTSIZE = 36;
	//Border widths and colors for score box.
	var SCOREBOXBORDER = 5;
	var SCORETEXTBORDER = 3;
	var SCOREBOXCOLOR = "rgba(0,0,0,0.7)";
	var SCORETEXTSIZE = 32;
	//Same for viruses.
	var VIRUSCOLOR = "#33FF33";
	var VIRUSBORDERCOLOR = "#2EE62E";
	var VIRUSRADIUS = 100;
	//The mass that is ejected at once.
	var EJECTMASS = 16;
	//Dimensions of the map.
	var MAPWIDTH = 10000;
	var MAPHEIGHT = 10000;

	var users = [];
	//A list of foods (the small dots you see on the map).
	var foods = [];
	//The userId and user object of the user for this player.
	var userId;
	var user;
	//A list of viruses (green spiky things).
	var viruses = [];
	//A list of all ejects mass blobs
	var ejects = [];
	var angle;
	//Total mass of all cells for this user.
	var totalMass;

	//Grab the canvas and prepare the context.
	var canvas = document.getElementById('game-canvas');
	var context = canvas.getContext("2d");
	//Grab the playerName.
	var playerName = playerNameInput.value;
	//The last frame updated with requestAnimationFrame().
	var lastFrameId;
	//The score of the player, which is the maximum totalMass.
	var score = STARTMASS;

	/*
	//Remove the gray background of all elements in the first run.
	//When the player dies afterwards, the background is his/her last view.
	$('body').css({"background-color": "rgba(0,0,0,0)"});
	$('html').css({"background-color": "rgba(0,0,0,0)"});
	*/

	//Connect to the server.
	var socket = io.connect();

	//Greet the server by givini it playerName.
	socket.emit('client-greet',playerName);

	//Get the user object given its id.
	var getUserById = function(id){
		for (var i = 0; i < users.length; ++i)
			if (users[i].userId == id)
				return users[i];
	}

	/*
	When the server greets the client:
	 - data.users: list of the users.
	 - data.userId: userId of the player.
	 - data.foods
	 - data.viruses
	*/
	socket.on('server-greet',function(data){
		users = data.users;
		userId = data.userId;
		//Get the local user.
		user = getUserById(userId);
		//Set the overall position of the user to that of the cell.
		user.posX = user.cells[0].posX;
		user.posY = user.cells[0].posY;
		foods = data.foods;
		viruses = data.viruses;
	});

	/*
	The server tells the client a new client has joined:
	 - user: The new user object.
	*/
	socket.on('new-client',function(user){
		//If it's not this user, add it to the list.
		if (user.userId != userId)
			users.push(user);
	});

	/*
	The server tells the client a player has disconnected.
	 - data: the userId of the disconnected player.
	*/
	socket.on('player-disconnect',function(data){
		//Delete the user from the list.
		for (var i = 0; i < users.length; ++i)
			if (users[i].userId == data.userId)
				users.splice(i,1);
	});

	/*
	Player update from the server.
	 - data.userId: The user that updated.
	 - data.cells: Cells for that user.
	*/
	socket.on('update-from-server',function(data){
		var user = getUserById(data.userId);
		if (user != null)
			user.cells = data.cells;
	});

	/*
	A food is eaten.
	 - data.food: index of the food.
	*/
	socket.on('food-eaten',function(data){
		foods.splice(data.food,1);
	});

	//Updates for food, viruses, ejects.
	socket.on('foods-update',function(data){
		foods = data;
	});

	socket.on('viruses-update',function(data){
		viruses = data;
	});

	socket.on('ejects-update',function(data){
		ejects = data;
	});

	/*
	The server tells the client a player died.
	 - id: the userid of that player.
	*/
	socket.on('client-died',function(id){
		//If the id matches ours:
		if (id === userId){
			//Stop animating.
			cancelAnimationFrame(lastFrameId);
			//Bring up the menu again.
			runStartMenu(restartAfterDeath);
		}
	});

	//Get the mouse position.
	var getMousePosition = function(event){
		var x;
		var y;
		if (event.pageX || event.pageY){
			x = event.pageX;
			y = event.pageY;
		}
		else{
			x = event.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
			y = event.clientY + document.body.scrollTop + document.documentElement.scrollTop;
		}
		x -= canvas.offsetLeft;
		y -= canvas.offsetTop;
		return {posX: x, posY: y};
	}

	//Functions used for scaling and unscaling lengths.
	var scaleLength = function(length){
		return length * STARTMASS / totalMass;
	}

	var unscaleLength = function(length){
		return length * totalMass / STARTMASS;
	}

	var logScaleLength = function(length){
		return length * Math.log10(STARTMASS) / Math.log10(totalMass);
	}

	var logUnscaleLength = function(length){
		return length * Math.log10(totalMass) / Math.log10(STARTMASS);
	}

	//Restart the game after the player's death.
	var restartAfterDeath = function(){
		//Get the new name of the player.
		playerName = playerNameInput.value;
		//Tell the server that the player wants to rejoin.
		socket.emit('player-respawn',playerName);
		//Start animating the canvas again.
		drawLoop();
	}

	var drawLoop = function(){
		//requestAniationFrame for silky smooth animation.
		lastFrameId = requestAnimationFrame(drawLoop);
		
		//If we haven't made contact with the server, don't do anything this drawLoop.
		if (user == null) return;
		
		//Ready canvas.
		//Set the dimensions of the canvas to that of the window.
		canvas.width = window.innerWidth;
		canvas.height = window.innerHeight;
		//Fill the canvas with the background color.
		context.fillStyle = "#F2FCFE";
		context.fillRect(0,0,canvas.width,canvas.height);

		//Calculate centre of all cells of user and total mass.
		user.posX = user.posY = 0;
		totalMass = 0;
		for (var i = 0; i < user.cells.length; ++i){
			user.posX += user.cells[i].posX;
			user.posY += user.cells[i].posY;
			totalMass += user.cells[i].mass;
		}
		user.posX /= user.cells.length;
		user.posY /= user.cells.length;
		
		/*
		A lot of the drawing functions aren't commented because they are mostly just setting color, font, width, etc.
		*/

		//Stroke gridlines.
		context.strokeStyle = "#D6DFE4";
		//The gridlines start at (0,0). We find the offset.
		var offsetX = Math.ceil(user.posX/TILEWIDTH) * TILEWIDTH - user.posX;
		var offsetY = Math.ceil(user.posY/TILEWIDTH) * TILEWIDTH - user.posY;
		
		//From all directions from the player, we stroke gridlines at that offset with a scaled distance.
	
		//Horizontal gridlines:
		for (var y = logScaleLength(offsetY) + canvas.height/2; y <= canvas.height; y += logScaleLength(TILEWIDTH)){
			context.beginPath();
			context.moveTo(0,y);
			context.lineTo(canvas.width,y);
			context.stroke();
		}
		for (var y = canvas.height/2 - logScaleLength(TILEWIDTH - offsetY); y >= 0; y -= logScaleLength(TILEWIDTH)){
			context.beginPath();
			context.moveTo(0,y);
			context.lineTo(canvas.width,y);
			context.stroke();
		}

		//Vertical gridlines:
		for (var x = logScaleLength(offsetX) + canvas.width/2; x <= canvas.width; x += logScaleLength(TILEWIDTH)){
			context.beginPath();
			context.moveTo(x,0);
			context.lineTo(x,canvas.height);
			context.stroke();
		}
		for (var x = canvas.width/2 - logScaleLength(TILEWIDTH - offsetX); x >= 0; x -= logScaleLength(TILEWIDTH)){
			context.beginPath();
			context.moveTo(x,0);
			context.lineTo(x,canvas.height);
			context.stroke();
		}

		//Stroke the limits of the map.
		context.strokeStyle = "black";

		context.beginPath();
		context.moveTo(canvas.width/2-logScaleLength(user.posX),canvas.height/2-logScaleLength(user.posY));
		context.lineTo(canvas.width/2-logScaleLength(user.posX),canvas.height/2+logScaleLength(MAPHEIGHT-user.posY));
		context.stroke();

		context.beginPath();
		context.moveTo(canvas.width/2-logScaleLength(user.posX),canvas.height/2-logScaleLength(user.posY));
		context.lineTo(canvas.width/2+logScaleLength(MAPWIDTH-user.posX),canvas.height/2-logScaleLength(user.posY));
		context.stroke();

		context.beginPath();
		context.moveTo(canvas.width/2+logScaleLength(MAPWIDTH-user.posX),canvas.height/2-logScaleLength(user.posY));
		context.lineTo(canvas.width/2+logScaleLength(MAPWIDTH-user.posX),canvas.height/2+logScaleLength(MAPHEIGHT-user.posY));
		context.stroke();

		context.beginPath();
		context.moveTo(canvas.width/2-logScaleLength(user.posX),canvas.height/2+logScaleLength(MAPHEIGHT-user.posY));
		context.lineTo(canvas.width/2+logScaleLength(MAPWIDTH-user.posX),canvas.height/2+logScaleLength(MAPHEIGHT-user.posY));
		context.stroke();

		//Draw on the foods onto the canvas.
		for (var i = 0; i < foods.length; ++i){
			//If the food is within the fov of the canvas (checking with scale):
			if (user.posX - logUnscaleLength(canvas.width/2) - 2*FOODRADIUS <= foods[i].posX &&
				foods[i].posX <= user.posX + logUnscaleLength(canvas.width/2) + 2*FOODRADIUS &&
				user.posY - logUnscaleLength(canvas.height/2) - 2*FOODRADIUS <= foods[i].posY &&
				foods[i].posY <= user.posY + logUnscaleLength(canvas.height/2) + 2*FOODRADIUS){
				//Set the color of the food particle.
				context.fillStyle = 'hsl(' + foods[i].hue + ',80%,40%)';
				//Draw on a circle with scaling at that color.
				context.beginPath();
				context.arc(canvas.width/2 + logScaleLength(foods[i].posX - user.posX), canvas.height/2 + logScaleLength(foods[i].posY - user.posY), logScaleLength(FOODRADIUS),0,2*Math.PI,false);
				context.fill();
				//context.stroke();
			}
		}

		//Draw all ejected masses.
		for (var i = 0; i < ejects.length; ++i){
			//Set the color of the eject.
			context.fillStyle = 'hsl(' + ejects[i].hue + ',80%,40%)';
			//Draw on a circle with the color.
			context.beginPath();
			context.arc(canvas.width/2 + logScaleLength(ejects[i].posX - user.posX), canvas.height/2 + logScaleLength(ejects[i].posY - user.posY),logScaleLength(EJECTMASS*2),0,2*Math.PI,false);
			context.fill();
		}

		//A list of all the cells of all users.
		//This is used so that smaller cells are drawn under bigger cells.
		var allCells = [];
		for (var i = 0; i < users.length; ++i)
			for (var j = 0; j < users[i].cells.length; ++j)
				allCells.push(users[i].cells[j]);

		//Sort the cells increasing by mass.
		allCells.sort(function(a,b){
			return a.mass - b.mass;
		});

		//Draw on the cells, stopping to draw on viruses when you can.
		var virusIndex = 0;
		for (var i = 0; i < allCells.length; ++i){
			//If there are viruses to draw:
			if (viruses.length > 0 && virusIndex < viruses.length){
				//If this cell is the first cell to be larger than virus[virusIndex], blit on the image of a virus (scaled).
				if (2*allCells[i].mass > VIRUSRADIUS + viruses[virusIndex].mass){
					context.drawImage(virusImage, canvas.width/2 + logScaleLength(viruses[virusIndex].posX - user.posX) - logScaleLength(VIRUSRADIUS + viruses[virusIndex].mass)/2, canvas.height/2 + logScaleLength(viruses[virusIndex].posY - user.posY) - logScaleLength(VIRUSRADIUS + viruses[virusIndex].mass) / 2, logScaleLength(VIRUSRADIUS + viruses[virusIndex].mass) * 2, logScaleLength(VIRUSRADIUS + viruses[virusIndex].mass) * 2);
					++virusIndex;
				}
			}

			//If the user is within the fov of the canvas:
			if (user.posX - logUnscaleLength(canvas.width/2) - allCells[i].mass*4 <= allCells[i].posX &&
				allCells[i].posX <= user.posX + logUnscaleLength(canvas.width/2) + allCells[i].mass*4 &&
				user.posY - logUnscaleLength(canvas.height/2) - allCells[i].mass*4 <= allCells[i].posY &&
				allCells[i].posY <= user.posY + logUnscaleLength(canvas.height/2) + allCells[i].mass*4){

				//Draw on teh cell and outline it with colors.
				context.lineWidth = CELLBORDERWIDTH;
				context.fillStyle = 'hsl(' + getUserById(allCells[i].userId).hue + ',80%,40%)';
				context.strokeStyle = 'hsl(' + getUserById(allCells[i].userId).hue + ',70%,50%)';
				context.beginPath();
				context.arc(canvas.width/2 + logScaleLength(allCells[i].posX - user.posX), canvas.height/2 + logScaleLength(allCells[i].posY - user.posY),logScaleLength(allCells[i].mass*2),0,2*Math.PI,false);
				context.fill();
				context.stroke();

				//Draw on the name of the cell:
				var fontSize = Math.max(logScaleLength(allCells[i].mass),MINFONTSIZE);
				context.lineWidth = logScaleLength(TEXTBORDERWIDTH);
				context.textAlign = 'center';
				context.textBaseline = 'middle';
				context.font = 'bold ' + fontSize + 'px sans-serif';
				context.fillStyle = "#FFFFFF";
				context.strokeStyle = "#000000";
				context.fillText(getUserById(allCells[i].userId).name, logScaleLength(allCells[i].posX - user.posX) + canvas.width/2, logScaleLength(allCells[i].posY - user.posY) + canvas.height/2);
				context.strokeText(getUserById(allCells[i].userId).name, logScaleLength(allCells[i].posX - user.posX) + canvas.width/2, logScaleLength(allCells[i].posY - user.posY) + canvas.height/2);
			}
		}

		//Draw on all of the viruses that are larger than all the cells.
		for (var i = virusIndex; i < viruses.length; ++i){
			context.drawImage(virusImage, canvas.width/2 + logScaleLength(viruses[virusIndex].posX - user.posX) - logScaleLength(VIRUSRADIUS + viruses[virusIndex].mass)/2, canvas.height/2 + logScaleLength(viruses[virusIndex].posY - user.posY) - logScaleLength(VIRUSRADIUS + viruses[virusIndex].mass) / 2, logScaleLength(VIRUSRADIUS + viruses[virusIndex].mass) * 2, logScaleLength(VIRUSRADIUS + viruses[virusIndex].mass) * 2);
			virusIndex++;
		}

		//Draw on the scorebox, at a certain border.
		context.textAlign = 'left';
		context.textBaseline = 'bottom';
		score = Math.max(score,Math.round(totalMass));
		var scoreText = "Score: " + score;
		context.font = "bold " + SCORETEXTSIZE + "px sans-serif"
		var scoreDimensions = context.measureText(scoreText);
		context.fillStyle = SCOREBOXCOLOR;
		context.fillRect(SCOREBOXBORDER, canvas.height - SCORETEXTSIZE - SCOREBOXBORDER - SCORETEXTBORDER, scoreDimensions.width + 2 * SCORETEXTBORDER, SCORETEXTSIZE + 2 * SCORETEXTBORDER);
		context.fillStyle = "#FFFFFF";
		context.fillText(scoreText, SCOREBOXBORDER + SCORETEXTBORDER, canvas.height - SCOREBOXBORDER + SCORETEXTBORDER);
		
		//Update the angle of the mouse to the user.
		socket.emit('update-from-client',angle);
	}

	//The function called when the mouse is moved.
	var moveFunc = function(event){
		//Update the angle of the mouse from the center of the screen (where the user's cells are).
		var mouse = getMousePosition(event);
		angle = Math.atan2(mouse.posY - canvas.height/2, mouse.posX - canvas.width/2);
	}

	//The function called when a key is pressed.
	var keyFunc = function(event){
		//If entered is pressed, the player wants to split.
		if (event.keyCode == 32)
			socket.emit("split-by-client",angle);
		//If w is pressed, the player wants to eject.
		else if (event.keyCode == 87)
			socket.emit("eject-by-client",angle);

		/*
		Debug code to tell the server to increase the mass of the cell.
		else if (event.keyCode == 65)
			socket.emit("debug-incr");
		*/
	}

	//Add the listeners to the window to listen for events.
	window.addEventListener('mousemove',moveFunc,false);
	window.addEventListener('keydown',keyFunc,false);

	//Call the first instance of the recursive drawLoop.
	drawLoop();
}

//Show the startMenu.
var showMenu = function(){
	//Ready the startMenuWrapper and make z-index = 1 so the user can interact with it.
	$('#startMenuWrapper').css({"z-index": 1, "position": "static"});
	//Hide the gameAreaWrapper.
	$("#gameAreaWrapper").css({"display": "none"});
	//Slowly increase the opacity of the startMenuWrapper.
	$('#startMenuWrapper').stop().animate({"opacity": 1}, 100);
}

//Hide the startMenu.
var hideMenu = function(){
	//Remove focus from all textboxes.
	$('input').blur();
	//Show the gameAreaWrapper.
	$("#gameAreaWrapper").css({"display": "block"});
	//Hide the startMenuWrapper, and change its z-index so it won't be affected when the user is playing.
	$('#startMenuWrapper').css({"opacity": 0, "z-index": -1, "position": "fixed"});
}

/*
Run the startMenu.
 - callBack: The function to call when runStartMenu is finished.
*/
var runStartMenu = function(callBack){
	//Get button, errorText objects from the document.
	var button = document.getElementById('startButton'),
	playerNameErrorText = document.querySelector('#startMenu .input-error');

	showMenu();
	
	//If the player clicks the button or presses enter, check if the name is valid.
	//If it is, hide the menu, start the game with the playerName used.
	//Otherwise, show the playerNameErrorText.
	
	button.onclick = function(){
		if (validPlayerName()){
			callBack();
			hideMenu();
		}
		else
			playerNameErrorText.style.display = 'inline';
	};
	
	playerNameInput.addEventListener('keypress',function(e){
		//If the player presses enter:
		var key = e.which || e.keyCode;
		if (key === 13){
			if (validPlayerName()){
				callBack();
				hideMenu();
			}
			else
				playerNameErrorText.style.display = 'inline';
		}	
	});
}

//When the window is loaded, start the game.
window.onload = function() {
	runStartMenu(runGame);
}
