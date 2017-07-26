#builds the jar file.
#shell script because i dont want to learn makefiles.

rm -rf com
mkdir com
mkdir com/ics4u
javac -d . src/com/ics4u/*.java
cp src/com/ics4u/pokemon.txt com/ics4u/
jar cvfm PokemonArena.jar META-INF/MANIFEST.MF com
