import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import javax.swing.*;

import java.io.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

//Object for the starting menu of the game.
public class TronMenuPanel extends JPanel{
	
	private TronGame tronGame;
	private InputHandler inputHandler;

	private BufferedImage background;		//BufferedImage of the background.

	//Which choice they are currently on.
	private int selection = 0;
	//0 - Play
	//1 - Quit
	//2 - Instructions
	//If the players choose play, they will be taken to instructions.
	private static final int 
			SELECTION_PLAY = 0,
			SELECTION_QUIT = 1,
			SELECTION_INSTR = 2;

	private Color fgColor = new Color(23,23,23),		//foreground color
			bgColor,									//background color
			player2Color = new Color(160,220,231),		//color for player 2's bike
			player1Color = new Color(248,198,48);		//color for player 1's bike
	private boolean isReady = false;

	private int lastWinner;
	
	//Constructor.
	//tronGame: Pointer to TronGame object
	//inputHandler: Points to InputHandler object
	//bgFileName: File name for background image
	//lastWinner: The winner of the previous game. 0 : player 1, 1: player 2.
	public TronMenuPanel(TronGame tronGame, InputHandler inputHandler, String bgFileName, int lastWinner){
		this.tronGame = tronGame;
		this.inputHandler = inputHandler;
		setSize(800,600);
		setFocusable(true);

		//Try to open the background image.
		try{
			background = ImageIO.read(new File(bgFileName));
		}
		catch (IOException e){
			e.printStackTrace();
			System.exit(0);
		}

		//Change the color of the foreground to the player that has just won.
		this.lastWinner = lastWinner;
		if (lastWinner == 0){
			this.fgColor = player1Color;
		}
		else if (lastWinner == 1){
			this.fgColor = player2Color;
		}
	}

	protected void paintComponent(Graphics g){
		//Convert to Graphics2D first
		Graphics2D g2 = (Graphics2D) g;

		//If we are not in the instructions phase:
		if (selection != 2){
			//Blit on the background image.
			g2.drawImage(background, null, 0, 0);

			//Draw in title "java_tron".
			g2.setColor(fgColor);
			g2.setFont(new Font("Courier", Font.PLAIN, 48)); 
			drawStringCentered(g2,"java_tron",800,0,350);
			g2.setFont(new Font("Courier", Font.PLAIN, 32)); 

			//Draw the options: play (selection == 0) or quit (selection == 1).
			//Draw the string with -'s if it is the current selection.
			if (selection == 0){
				drawStringCentered(g2,"- play -",800,0,420);
			}
			else{
				drawStringCentered(g2,"play",800,0,420);
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
		else{
			//Draw out instructions and controls. Very messy.
			
			g2.setColor(bgColor);
			g2.fillRect(0,0,800,600);
			
			//Set it to player 1's color, and draw in WASD for movement and Q for boost.
			g2.setColor(player1Color);
			g2.setFont(new Font("Courier", Font.PLAIN, 32)); 
			drawStringCentered(g2,"move",400,5,120);
			g2.drawRect(170,140,70,70);
			drawStringCentered(g2,"W",20,175,165);
			g2.drawRect(95,215,70,70);
			drawStringCentered(g2,"A",20,100,240);
			g2.drawRect(170,215,70,70);
			drawStringCentered(g2,"S",20,175,240);
			g2.drawRect(245,215,70,70);
			drawStringCentered(g2,"D",20,250,240);
			drawStringCentered(g2,"boost",400,5,350);
			g2.drawRect(170,370,70,70);
			drawStringCentered(g2,"Q",20,175,395);

			//Set it to player 2's color, and do similar things.
			g2.setColor(player2Color);
			drawStringCentered(g2,"move",400,405,120);
			g2.drawRect(570,140,70,70);
			drawStringCentered(g2,"U",20,575,165);
			g2.drawRect(495,215,70,70);
			drawStringCentered(g2,"L",20,500,240);
			g2.drawRect(570,215,70,70);
			drawStringCentered(g2,"D",20,575,240);
			g2.drawRect(645,215,70,70);
			drawStringCentered(g2,"R",20,650,240);
			drawStringCentered(g2,"boost",400,405,350);
			g2.drawRect(535,370,140,70);
			g2.setFont(new Font("Courier", Font.PLAIN, 32)); 
			drawStringCentered(g2,"ENTER",140,535,415);		

			//Set the color to gray and print out what to do.
			g2.setFont(new Font("Courier", Font.PLAIN, 16)); 
			g2.setColor(new Color(150,150,150));
			drawStringCentered(g2,"first_to_five_wins",800,0,490);
			drawStringCentered(g2,"press_space_to_continue",800,0,520);
		}
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

	public void tick(){
		//If we are not in instructions phase:
		if (selection != 2){
			//Allow the users to select "play" with W or UP.
			if (inputHandler.keys[KeyEvent.VK_UP] == 2 || inputHandler.keys[KeyEvent.VK_W] == 2){
				selection = SELECTION_PLAY;
			}
			//Or select "quit" with S or DOWN.
			else if (inputHandler.keys[KeyEvent.VK_DOWN] == 2 || inputHandler.keys[KeyEvent.VK_S] == 2){
				selection = SELECTION_QUIT;
			}
		}
		//If the space bar is pressed (seletcion chosen):
		if (inputHandler.keys[KeyEvent.VK_SPACE] == 2){
			Sound.beep.play();			//Play a beep sound.
			//If the selection is play:
			if (selection == SELECTION_PLAY){
				//Set the selection to instructions.
				selection = SELECTION_INSTR;
			}
			//If the selection is quit:
			else if (selection == SELECTION_QUIT){
				System.exit(0);
			}
			//If the selection is instructions:
			else if (selection == SELECTION_INSTR){
				//Start the game.
				tronGame.startGamePanel();
			}
		}
	}

	//Add notify to avoid pesky NullPointerExceptions
	public void addNotify(){
		super.addNotify();
		isReady = true;
	}
	
	public boolean getIsReady(){
		return isReady;
	}
	
}
