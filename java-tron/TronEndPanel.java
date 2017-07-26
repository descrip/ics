import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import javax.swing.*;

import java.io.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

//Ending JPanel. Shown when the players have finished the game and one has won.
//A lot is copied from TronMenuPanel.
public class TronEndPanel extends JPanel{
	
	private TronGame tronGame;
	private InputHandler inputHandler;

	//BufferedImage of the background.
	private BufferedImage background;
	//Current selected option.
	private int selection = 0;
	private static final int 
		SELECTION_RESTART = 0,
		SELECTION_QUIT = 1;

	private Color fgColor, 
			bgColor,
			player1Color,
			player2Color;
	private boolean isReady = false;

	private int player1Score, player2Score;		//Scores of the two players.
	
	//Constructor.
	//tronGame: pointer to TronGame object.
	//inputHandler: pointer to InputHandler object.
	//bgFileName: String for the background image file name.
	//fgColor: foreground color.
	//player1Score, player2Score: scores for the two players.
	public TronEndPanel(TronGame tronGame, InputHandler inputHandler, String bgFileName, Color fgColor, int player1Score, int player2Score){
		this.tronGame = tronGame;
		this.inputHandler = inputHandler;
		setSize(800,600);
		setFocusable(true);

		//Try to load the background.
		try{
			background = ImageIO.read(new File(bgFileName));
		}
		catch (IOException e){
			e.printStackTrace();
			System.exit(0);
		}

		this.bgColor = new Color(23,23,23);
		this.fgColor = fgColor;

		this.player1Score = player1Score;
		this.player2Score = player2Score;
	}

	//Paint contents of this JPanel.
	protected void paintComponent(Graphics g){
		//Convert to Graphics2D object.
		Graphics2D g2 = (Graphics2D) g;

		//Draw in the background.
		g2.drawImage(background, null, 0, 0);

		//Print out who wins.
		g2.setColor(fgColor);
		g2.setFont(new Font("Courier", Font.PLAIN, 48)); 
		if (player1Score < player2Score){
			drawStringCentered(g2,"right_wins",800,0,350);
		}
		else{
			drawStringCentered(g2,"left_wins",800,0,350);
		}

		//Print out score.
		g2.setFont(new Font("Courier", Font.PLAIN, 32)); 
		drawStringCentered(g2,String.valueOf(player1Score) + ":" + String.valueOf(player2Score),800,0,310);

		//Print out options: restart, quit.
		//Print options with dashes if it is currently selected.
		if (selection == 0){
			drawStringCentered(g2,"- restart -",800,0,420);
		}
		else{
			drawStringCentered(g2,"restart",800,0,420);
		}

		if (selection == 1){
			drawStringCentered(g2,"- quit -",800,0,470);
		}
		else{
			drawStringCentered(g2,"quit",800,0,470);
		}

		g2.setFont(new Font("Courier", Font.PLAIN, 16)); 
		drawStringCentered(g2,"press_space_to_continue",800,0,520);
		drawStringCentered(g2,"made_by_jeffrey_zhao",800,0,550);
	}

	//Function to draw a string onto the JPanel centered, by width.
	//Takes in a width to center the string by, and coordinates for position.
	private void drawStringCentered(Graphics2D g2, String s, int width, int posX, int posY){
		//Find the length of the string with the current font.
        int stringLen = (int) g2.getFontMetrics().getStringBounds(s, g2).getWidth();
		//Draw it on with offset from that length.
        int start = width/2 - stringLen/2;
        g2.drawString(s, start + posX, posY);
	}

	//Update the TronEndPanel.
	public void tick(){
		//If a player has pressed W or UP, seclect "restart".
		if (inputHandler.keys[KeyEvent.VK_UP] == 2 || inputHandler.keys[KeyEvent.VK_W] == 2){
			selection = 0;
		}
		//If a player has pressed S or DOWN: select "quit".
		else if (inputHandler.keys[KeyEvent.VK_DOWN] == 2 || inputHandler.keys[KeyEvent.VK_S] == 2){
			selection = 1;
		}
		//If a player has presed space:
		if (inputHandler.keys[KeyEvent.VK_SPACE] == 2){
			Sound.beep.play();			//Play a beep sound.
			//If the selection is restart:
			if (selection == 0){
				//Clear the game scores and start the gamePanel.
				tronGame.clearScores();
				tronGame.startGamePanel();
			}
			//If the selection is quit:
			else if (selection == 1){
				System.exit(0);
			}
		}
	}

	public void addNotify(){
		super.addNotify();
		isReady = true;
	}
	
	public boolean getIsReady(){
		return isReady;
	}
	
}
