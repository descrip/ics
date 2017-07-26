import javax.sound.sampled.*;

//Class to play sounds.
//e.g. to play sound open, call Sound.open.play().
public class Sound {

	//Create static objects of all possible sounds in the game.
	public static Sound open = loadSound("res/open.wav");
	public static Sound beep = loadSound("res/beep.wav");
	public static Sound crash = loadSound("res/crash.wav");
	public static Sound music = loadSound("res/mus.wav");

	//Load a sound from a given file name.
	public static Sound loadSound(String fileName) {
		Sound sound = new Sound();
		try {
			AudioInputStream as = AudioSystem.getAudioInputStream(Sound.class.getResource(fileName));
			//Create a clip object for the new Sound object to play from.
			Clip clip = AudioSystem.getClip();
			clip.open(as);
			sound.clip = clip;
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(0);
		}
		return sound;
	}

	private Clip clip;

	//Play the sound.
	public void play() {
		try {
			//If we were successful in creating the clip:
			if (clip != null) {
				//Create a new thread to play the clip from.
				new Thread() {
					public void run() {
						synchronized (clip) {
							clip.stop();
							clip.setFramePosition(0);
							clip.start();
						}
					}
				}.start();
			}
		} catch (Exception e) {
			System.out.println(e);
			System.exit(0);
		}
	}

	//Loop the sound continuously.
	public void loop(){
		try {
			//If we were successful in creating the clip:
			if (clip != null) {
				//Create a new thread to play the clip from.
				//Loop it continuously.
				new Thread() {
					public void run() {
						synchronized (clip) {
							clip.stop();
							clip.setFramePosition(0);
							clip.loop(Clip.LOOP_CONTINUOUSLY);
						}
					}
				}.start();
			}
		} catch (Exception e) {
			System.out.println(e);
			System.exit(0);
		}
	}
}
