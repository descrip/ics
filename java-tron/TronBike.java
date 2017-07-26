import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import javax.swing.*;

//Class for a Tron Bike.
//There are two in a TronGamePanel.

//The "current line" is the line between the current position of the bike
//and the position of it's last turn.

public class TronBike{

	private TronGamePanel gamePanel;
	private int 
		posX, posY,					//Position
		dirX, dirY,					//Direction (vector)
		startSpeed,					//Initial speed
		numberOfLines,				//Number of lines we have
		numberOfBoosts = 3,			//Number of boosts the bike has remaining
		lastTurnX, lastTurnY;		//Position of the bikes last turn
	private double speed;			//Speed
	private Color bikeColor;		//Color
	public Line2D[] trail;			//Array of all lines in the bikes trail.
	
	//Constructor.
	//gamePanel: pointer to the TronGamePanel
	//(posX, posY): position
	//(dirX, dirY): direction
	//speed: speed
	//color: color
	public TronBike(TronGamePanel gamePanel, int posX, int posY, int dirX, int dirY, int speed, Color color){
		this.gamePanel = gamePanel;
		//Set both position and last turn to the given start position.
		this.posX = this.lastTurnX = posX;
		this.posY = this.lastTurnY = posY;
		this.dirX = dirX;
		this.dirY = dirY;
		//Set both the current speed and the intitial speed to the given intial speed.
		this.speed = this.startSpeed = speed;
		this.bikeColor = color;

		//Array of Line2D objects for the trail.
		//There are at most 800 x 600 = 480 000 lines.
		this.trail = new Line2D.Double[480000];
		this.numberOfLines = 0;		//Number of lines behind the current bike.
	}

	//Change the direction of the bike to whatever that is given.
	//Returns true if successful, false if not.
	public boolean changeDirection(int dirX, int dirY){
		//If the direction is perpendicular to the current one, change it.
		if ((this.dirY == 0 && dirY != 0) || (this.dirX == 0 && dirX != 0)){
			//Create a new Line2D object, since we are now breaking off this line.
			trail[numberOfLines] = new Line2D.Double(posX, posY, lastTurnX, lastTurnY);
			++numberOfLines;

			//Update the last turn positions and the directions.
			lastTurnX = posX;
			lastTurnY = posY;
			this.dirX = dirX;
			this.dirY = dirY;

			return true;
		}
		return false;
	}

	//Move the bike.
	public void move(){
		posX += dirX;
		posY += dirY;
	}

	//Boost the bike if there are any left. Doubles the speed of the bike.
	public void boost(){
		//If we have any boosts left and the speed is equal to the init speed:
		if (numberOfBoosts > 0 && speed == startSpeed){
			//Double the speed.
			speed = startSpeed * 2;
			//Decrease the counter.
			--numberOfBoosts;
			//Make the score slightly visible so players know how many boosts are left.
			gamePanel.setScoreTransparency(150);
		}
	}

	//See if the bike has collided with itself.
	//Returns true if it has, false if not.
	public boolean checkCollisionWithSelf(){
		//Going through all of the lines in the trail, check for a collision
		//between the current line.
		//Skip the last line in the trail because it shares a point with the current line,
		//and it is impossible to intersect with that line.
		for (int i = 0; i < numberOfLines-1; ++i){
			if (trail[i].intersectsLine(getCurrentLine())){
				return true;
			}
		}
		//See if the bike has collided with any boundaries.
		if (new Line2D.Double(0,0,800,0).ptSegDist(posX,posY) == 0.0 ||
			new Line2D.Double(0,0,0,600).ptSegDist(posX,posY) == 0.0 ||
			new Line2D.Double(0,600,800,600).ptSegDist(posX,posY) == 0.0 ||
			new Line2D.Double(800,0,800,600).ptSegDist(posX,posY) == 0.0){
			return true;
		}
		return false;
	}
	
	//See if the enemyBike has collided with this bike.
	//Returns true if yes, false if no.
	public boolean checkCollisionWith(TronBike enemyBike){
		//If the enemy bike has collided with the current line:
		//<= 1.0 is used to account for error, especially when boosting.
		if (new Line2D.Double(posX, posY, lastTurnX, lastTurnY).ptSegDist(enemyBike.getPosX(),enemyBike.getPosY()) <= 1.0){
			return true;
		}
		//If they share positions:
		if (posX == enemyBike.getPosX() && posY == enemyBike.getPosY()){
			return true;
		}
		//Go through every line in our trail and check if there is a collision.
		for (int i = 0; i < numberOfLines; ++i){
			if (trail[i].intersectsLine(enemyBike.getCurrentLine())){
				return true;
			}
		}
		return false;
	}

	//Return a Line2D object of the "current line".
	public Line2D getCurrentLine(){
		return new Line2D.Double(posX,posY,lastTurnX,lastTurnY);
	}

	//Decrease the speed of the bike by a bit if it is in a boost, to make it look smooth.
	public void decreaseSpeed(){
		speed = Math.max(startSpeed, speed-0.1);
	}

	public int getPosX(){
		return posX;
	}

	public int getPosY(){
		return posY;
	}

	public int getLastTurnX(){
		return lastTurnX;
	}
	
	public int getLastTurnY(){
		return lastTurnY;
	}

	public int getDirX(){
		return dirX;
	}

	public int getDirY(){
		return dirY;
	}

	public void setDirX(int what){
		dirX = what;
	}
	
	public void setDirY(int what){
		dirY = what;
	}
	
	public double getSpeed(){
		return speed;	
	}

	public int getStartSpeed(){
		return startSpeed;
	}
	
	public Color getColor(){
		return bikeColor;
	}
	
	public int getNumberOfLines(){
		return numberOfLines;
	}

	public int getNumberOfBoosts(){
		return numberOfBoosts;
	}
	
}
