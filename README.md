# Animation strip to USDZ converter

clip2usdz is a [Python](https://www.python.org/) command line tool for converting an animation strip to USDZ.  

## Prerequisites

### Animation strip

The animation strip image has to be organized into a grid with rows and columns.  

### Python Libraries

* The [Universal Scene Description](https://github.com/PixarAnimationStudios/USD) has to be build and the environment variables properly set.  
* Python Pillow: `pip install Pillow`  

## Executing the command line tool

Run `clip2usdz.py --help` for command line options. If no arguments are provided, the `Running Girl` asset is generated.   

```
-h, --help     show this help message and exit
-r ROWS        Number of rows of the animation strip.
-c COLUMNS     Number of columns of the animation strip.
-d DURATION    Duration in seconds.
-i IMAGENAME   Use another image beside the included animation strip.
-t TIMESTAMPS  Number of time stamps used per second.
-f FLANK       Value used to simulate a step interpolation.
```

## Assets

### Running Girl

[![](RunningGirl.png)](https://www.codeandweb.com/texturepacker/tutorials/how-to-create-a-sprite-sheet)  
`clip2usdz.py -r 1 -c 6 -d 1.0 -i RunningGirl.png`  

### Guitar Player

[![](GuitarPlayer.png)](https://polycount.com/discussion/98407/spriteplane-a-sprite-sheet-generator-script-for-photoshop)  
`clip2usdz.py -r 2 -c 3 -d 0.5 -i GuitarPlayer.png`  

