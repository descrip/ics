import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import javax.swing.*;

//Class used to handle key input from information given by the KeyRepeatSuppressor.
public class InputHandler{
	
	//Int array of the status of all keys.
	//key[code] = 2 means that key has just been pressed.
	//key[code] = 1 means that key is being held down.
	//key[code] = 0 means that key is not being pressed.
	public int[] keys = new int[65535];
	private KeyRepeatSuppressor suppressor;
	
	public InputHandler(KeyRepeatSuppressor suppressor){
		this.suppressor = suppressor;
	}
	
	public void tick(){
		int[] newKeys = new int[keys.length];
		//Get all of the keys that are being held down.
		for (int i : suppressor.getKeysDown()){
			//If i is not being pressed:
			if (keys[i] == 0){
				//Indicate it as just pressed.
				newKeys[i] = 2;
			}
			else{
				//Indicate it as being held down.
				newKeys[i] = 1;
			}
		}
		keys = newKeys;
	}

	public KeyRepeatSuppressor getSuppressor(){
		return suppressor;
	}

	//Make all key codes in the array indicate 0 (not being held down).
	public void clearKeys(){
		for (int i = 0; i < keys.length; ++i){
			keys[i] = 0;
		}
	}

	//Make all key codes in the array with 1 become 2.
	public void promoteKeys(){
		for (int i = 0; i < keys.length; ++i){
			if (keys[i] == 1){
				keys[i] = 2;
			}
		}
	}
	
}
