import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import javax.swing.*;

//Where a round of the game exists.
//A new TronGamePanel is made each round.
public class TronGamePanel extends JPanel {

	private TronGame tronGame;
	private TronBike[] playerBikes;
	private InputHandler inputHandler;

	//Alpha value of the scores.
	private int scoreTransparency = 255;
	//A quick counter to delay the start of the round for a bit. For dramatic effect.
	private int startWait = 60;

	//Constructor.
	public TronGamePanel(TronGame tronGame,InputHandler inputHandler){
		this.tronGame = tronGame;
		this.inputHandler = inputHandler;
		setSize(800,600);
		setFocusable(true);

		//Create the two TronBikes for the two players.
		//The first one is orange and starts at (100,300) with a direction of (1,0).
		//The second one is blue and starts at (700,300) with a direction of (-1,0).
		//Both have a speed of 4.
		playerBikes = new TronBike[] {new TronBike(this,100,300,1,0,4,new Color(248,198,48)), new TronBike(this,700,300,-1,0,4,new Color(160,220,231))};
	}

	//Paint on the contents of the JPanel.
	protected void paintComponent(Graphics g){
		//Convert g into a Graphics2D object first.
		Graphics2D g2 = (Graphics2D) g;

		//Fill in a gray background.
		g2.setColor(new Color(23,23,23));
		g2.fillRect(0,0,getWidth(),getHeight());

		//Draw the white grid lines.
		//They have both horizontal and vertical spacing of 50 px.
		g2.setStroke(new BasicStroke(1));
		g2.setColor(new Color(150,150,150));
		for (int i = 50; i < getWidth(); i += 50){
			g2.drawLine(0,i,getWidth(),i);
			g2.drawLine(i,0,i,getHeight());
		}

		g2.setStroke(new BasicStroke(4));
		//For each bike in the TronGamePanel:
		for (int i = 0; i < playerBikes.length; ++i){
			//Set color to current tron bike.		
			g2.setColor(playerBikes[i].getColor());

			//Draw each line in the trail of the tronBike.
			for (int j = 0; j < playerBikes[i].getNumberOfLines(); ++j){
				g2.draw(playerBikes[i].trail[j]);
			}
			//As well, draw the current line (the line that the bike is making right now).
			g2.drawLine(
					playerBikes[i].getPosX(),
					playerBikes[i].getPosY(),
					playerBikes[i].getLastTurnX(),
					playerBikes[i].getLastTurnY());
		}

		//If the alpha value of the score is greater than zero, draw it on.
		if (scoreTransparency > 0){
			g2.setColor(new Color(255,255,255,scoreTransparency));

			//Set the font to Monaco, 128 pt, and draw on a string for the scores, separated by spaces.
			g2.setFont(new Font("Monaco", Font.PLAIN, 128)); 
			drawStringCentered(g2,String.valueOf(tronGame.getPlayer1Score()) + 
					"             " + 
					String.valueOf(tronGame.getPlayer2Score()),600,100,497);
			
			//For each boost that player 1 has, draw a box to the right of his/her score.
			for (int i = 70, j = playerBikes[0].getNumberOfBoosts(); i > 0 && j > 0; i-=30, --j){
				g2.fillRect(60,400+i,20,20);
			}
			//Do the same, for player 2.
			for (int i = 70, j = playerBikes[1].getNumberOfBoosts(); i > 0 && j > 0; i-=30, --j){
				g2.fillRect(720,400+i,20,20);
			}
			
			//Decrease the alpha value to make the scores fade out over time.
			--scoreTransparency;
		}
	}

	//Function to draw a string onto the JPanel centered.
	//Takes in a width to center the string by, and coordinates for position.
	private void drawStringCentered(Graphics2D g2, String s, int width, int posX, int posY){
		//Find the length of the string with the current font.
        int stringLen = (int) g2.getFontMetrics().getStringBounds(s, g2).getWidth();
		//Draw it on with offset from that length.
        int start = width/2 - stringLen/2;
        g2.drawString(s, start + posX, posY);
	}

	//Update our TronGamePanel.
	public void tick(){
		//If the startWait counter is not zero:
		if (startWait == 0){
			//Handler the input from the players.
			handleInput();
			
			//Booleans if each player has won this round (if the other player has collided).
			boolean player1Win = false, 
					player2Win = false;
			
			//Update each bike by moving it.
			//This also checks for collisions from the other player.
			//The speed of the bike determines how many times it will loop.
			for (int i = 0; i < Math.min(playerBikes[0].getSpeed(),playerBikes[1].getSpeed()); ++i){
				player1Win = player1Win || moveBike(0);
				player2Win = player2Win || moveBike(1);
			}
			//If the speed of player 1 is greater than that of player 2's, update the rest separately.
			for (int i = 0; i < playerBikes[0].getSpeed() - playerBikes[1].getSpeed(); ++i){
				player1Win = player1Win || moveBike(0);
			}
			//Same for player 2.
			for (int i = 0; i < playerBikes[1].getSpeed() - playerBikes[0].getSpeed(); ++i){
				player2Win = player2Win || moveBike(1);
			}

			//If only one of the players win, update that score.
			//If there is a tie, then do not give a point to either player.
			if (player1Win && !player2Win){
				tronGame.winPlayer1();
			}
			else if (player2Win && !player1Win){
				tronGame.winPlayer2();
			}
			
			//If a player has reached maximum score, start the endPanel.
			if (tronGame.getPlayer1Score() == 5 || tronGame.getPlayer2Score() == 5){
				Sound.crash.play();			//Play a crashing sound.
				tronGame.startEndPanel();
			}
			//If a player has won a round, restart the gamePanel for a new round.
			else if (player1Win || player2Win){
				Sound.crash.play();			//Play a crashing sound.
				tronGame.restartGamePanel();
			}

			//If the speed of a playerBike is still being boosted, decrease it by a bit.
			playerBikes[0].decreaseSpeed();
			playerBikes[1].decreaseSpeed();
		}
		else{
			//Decrease the startWait counter.
			--startWait;
		}
	}

	public void setScoreTransparency(int what){
		scoreTransparency = what;
	}

	//Handle the input from the two players controlling the bikes.
	public void handleInput(){
		//For both players, only notice a press if they have just pressed that key.
		//i.e. inputHandler.keys[code] == 2.
		
		//Player 1: WASD to move.
		//If the bike successfully changes direction, exit the if structure.
		if (inputHandler.keys[KeyEvent.VK_W] == 2 && playerBikes[0].changeDirection(0,-1)){
		}
		else if (inputHandler.keys[KeyEvent.VK_A] == 2 && playerBikes[0].changeDirection(-1,0)){
		}
		else if (inputHandler.keys[KeyEvent.VK_S] == 2 && playerBikes[0].changeDirection(0,1)){
		}
		else if (inputHandler.keys[KeyEvent.VK_D] == 2 && playerBikes[0].changeDirection(1,0)){
		}

		//Player 2: Arrow keys to move.
		//If the bike successfully changes direction, exit the if structure.
		if (inputHandler.keys[KeyEvent.VK_UP] == 2 && playerBikes[1].changeDirection(0,-1)){
		}
		else if (inputHandler.keys[KeyEvent.VK_LEFT] == 2 && playerBikes[1].changeDirection(-1,0)){
		}
		else if (inputHandler.keys[KeyEvent.VK_DOWN] == 2 && playerBikes[1].changeDirection(0,1)){
		}
		else if (inputHandler.keys[KeyEvent.VK_RIGHT] == 2 && playerBikes[1].changeDirection(1,0)){
		}

		//Player 1: Q to boost.
		if (inputHandler.keys[KeyEvent.VK_Q] == 2){
			playerBikes[0].boost();
		}
		//Player 2: Enter to boost.
		if (inputHandler.keys[KeyEvent.VK_ENTER] == 2){
			playerBikes[1].boost();
		}
	}

	//Move a given bike.
	//0: player 1
	//1: player 2
	//returns true if there is a collision from the other bike.
	public boolean moveBike(int what){
		//Move.
		playerBikes[what].move();
		
		//Check for a collision.
		if (playerBikes[what].checkCollisionWith(playerBikes[1-what]) ||
			playerBikes[1-what].checkCollisionWithSelf()){
			return true;
		}

		return false;
	}
}
