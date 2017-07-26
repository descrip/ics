import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import javax.swing.*;

//Main class.
public class TronGame extends JFrame implements Runnable{

    private static final long serialVersionUID = 1L;

	private String windowName;

	//Multiple panels for the JFrame to show.
	private TronGamePanel gamePanel;
	private TronMenuPanel menuPanel;
	private TronEndPanel endPanel;
	//The player starts with the menuPanel, then gamePanel, then endPanel.

	private InputHandler inputHandler;
	private KeyRepeatSuppressor suppressor;

	private boolean isRunning;	//If the program is running.
	//Flags to indicate if individual JPanels are running.
	private boolean isGameRunning = false, isMenuRunning = true, isEndRunning = false;
	private Thread thread;		//Thread for the TronGame.

	//Scores for both players.
	private int player1Score, player2Score;
	//The game is won by the first who reaches five.

	public static void main(String[] args){
		//Create a TronGame object and start a thread for it.
		//If we can't start a thread, try again until we can.
		TronGame game = new TronGame("Java Tron");
		while (true){
			if (game.start()){
				break;
			}
		}
	}

	public TronGame(String windowName){
		//Name the window.
		super(windowName);
		this.windowName = windowName;

		//Create a KeyRepeatSuppressor and pass it to the InputHandler.
		try{
			suppressor = new KeyRepeatSuppressor();
			this.inputHandler = new InputHandler(suppressor);
		}
		catch (AWTException e){
			e.printStackTrace();
			System.exit(-1);
		}

		//Create menuPanel. Player first uses the menuPanel.
		this.menuPanel = new TronMenuPanel(this,inputHandler,"res/menu.png",1);
		this.gamePanel = new TronGamePanel(this,inputHandler);

		setSize(800,600);
		add(menuPanel);

		//Install the KeyRepeatSuppressor. Pretty much addKeyListener.
		suppressor.installTo(this);
		
		//Make close operation be actually closing the window.
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		//Make the window not resizable.
		setResizable(false);
		//Make the window visible.
		setVisible(true);

		//Start looping the music.
		Sound.music.loop();
	}

	//Start a thread for the TronGame.
	//Returns true if it started properly, false otherwise.
	public synchronized boolean start(){
		//If the program is already running or the menuPanel is not ready:
		if (isRunning || !menuPanel.getIsReady()){
			return false;
		}
		else{
			//Create a new Thread object and mark it as running.
			isRunning = true;
			thread = new Thread(this);
			thread.start();
			return true;
		}
	}

	//Stop the thread for the TronGame.
	public synchronized void stop(){
		//If we are not running to begin with, return.
		if (!isRunning){
			return;
		}

		//Try to join the thread.
		try{
			thread.join();
		}
		catch (InterruptedException ex){
			ex.printStackTrace();
			System.exit(0);
		}
	}

	//Method called by the TronGame thread. Most of the activity takes place here.
	public void run(){
		int frames = 0;			//Number of frames gone past, used in fps.

		
		//The amount of time we have to tick.
		double unprocessedSeconds = 0;		
		long lastTime = System.nanoTime();
		
		//Number of seconds per tick. fps is the reciprocal.
		//Right now we are only allowing 60 fps.
		double secondsPerTick = 1 / 60.0;
		
		//The number of ticks we have gone through.
		int tickCount = 0;

		requestFocus();
		
		while (isRunning){
			//Find unproccessedSeconds.
			long now = System.nanoTime();
			long passedTime = now - lastTime;
			lastTime = now;
			if (passedTime < 0){		//YEAH TIME TRAVELLING
				passedTime = 0;
			}
			if (passedTime > 1000000000){
				passedTime = 1000000000;
			}

			unprocessedSeconds += passedTime / 1000000000.0;

			boolean ticked = false;
			//While we still have seconds we can process and not go over our fps:
			while (unprocessedSeconds > secondsPerTick){
				inputHandler.tick();	//Update our inputHandler

				//Update whichever panel that is running right now.
				if (isMenuRunning){
					menuPanel.tick();
				}
				else if (isGameRunning){
					gamePanel.tick();
				}
				else if (isEndRunning){
					endPanel.tick();
				}

				//Decrease the seconds we used, and marked that we ticked.
				unprocessedSeconds -= secondsPerTick;
				ticked = true;

				++tickCount;
				//If we've ticked enough print out fps.
				if (tickCount % 60 == 0){
					System.out.println(frames + " fps");
					lastTime += 1000;
					frames = 0;
				}
			}

			//If we've ticked, repaint the active panel and +1 frames.
			if (ticked){
				if (isMenuRunning){
					menuPanel.repaint();
				}
				else if (isGameRunning){
					gamePanel.repaint();
				}
				else if (isEndRunning){
					endPanel.repaint();
				}
				++frames;
			}
			//Otherwise, try sleeping the thread.
			else{
				try{
					Thread.sleep(1);
				}
				catch (InterruptedException e){
					e.printStackTrace();
					System.exit(0);
				}
			}
		}
	}

	//Add one to the score of player 1.
	public void winPlayer1(){
		++player1Score;
	}

	//Add one to the score of player 2.
	public void winPlayer2(){
		++player2Score;
	}

	public int getPlayer2Score(){
		return player2Score;
	}
	
	public int getPlayer1Score(){
		return player1Score;
	}

	//Reset the scores for both players.
	public void clearScores(){
		player1Score = 0;
		player2Score = 0;
	}

	//Called by menuPanel to start the gamePanel.
	public void startGamePanel(){
		isGameRunning = true;
		isMenuRunning = false;
		isEndRunning = false;
		restartGamePanel();
		Sound.open.play();	//Play a cool sound.
	}
	
	//Restart our gamePanel by replacing it with a new one.
	//Called by the current gamePanel whenever a round is over.
	public void restartGamePanel(){
		gamePanel.repaint();	//Repaint it one last time.
		
		//Wait a bit for the players to soak in the previous round.
		try{
			thread.sleep(750);
		}
		catch (InterruptedException e){
			e.printStackTrace();
			System.exit(0);
		}

		//Clear the keys for the new round.
		inputHandler.clearKeys();
		//Remove all the JPanels the JFrame currently carries,
		//And replace it with a new one.
		getContentPane().removeAll();
		gamePanel = new TronGamePanel(this,inputHandler);
		add(gamePanel);
	}

	//Start the endPanel.
	//Called by the current gamePanel when a player has reached five points.
	//Very similar to restartGamePanel().
	public void startEndPanel(){
		gamePanel.repaint();	//Repaint the gamePanel one last time.
		
		//Wait a bit for the players to soak in the entire game.
		try{
			thread.sleep(750);
		}
		catch (InterruptedException e){
			e.printStackTrace();
			System.exit(0);
		}
		
		//Clear the keys and remove all JPanels in the JFrame.
		inputHandler.clearKeys();
		getContentPane().removeAll();

		//Add different arguments to the endPanel to display different colors based on the winner.
		if (player1Score == 5){
			endPanel = new TronEndPanel(this,inputHandler,"res/menu2.png",new Color (248,198,48), player1Score, player2Score);
		}
		else if (player2Score == 5){
			endPanel = new TronEndPanel(this,inputHandler,"res/menu.png",new Color (160,220,231), player1Score, player2Score);
		}

		//Add the endPanel and flip some flags.
		add(endPanel);
		isGameRunning = false;
		isEndRunning = true;
	}
}
