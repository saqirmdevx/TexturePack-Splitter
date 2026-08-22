### Task:

Context:

- We need to create a Spritesheet splitter application, it can be either in Python or NodeJs.

It should take input as:

- spritesheet.json
- spritesheet.png

and should split it to separate frames and also into folders based on animations and name each frame exactly as described in Spritesheet.json

In Spritesheet it is decrribed as following:
"animations": {
"Attack": ["Attack/0.png","Attack/1.png","Attack/2.png"],
"Death": ["Death/0.png","Death/1.png","Death/2.png","Death/3.png","Death/4.png","Death/5.png","Death/6.png","Death/7.png","Death/8.png","Death/9.png","Death/10.png","Death/11.png","Death/12.png","Death/13.png","Death/14.png","Death/15.png"],
"Fall": ["Fall/0.png","Fall/1.png"],
"Idle": ["Idle/0.png","Idle/1.png","Idle/2.png"],
"Jump": ["Jump/0.png","Jump/1.png"],
"JumpApex": ["JumpApex/0.png","JumpApex/1.png","JumpApex/2.png"],
"Land": ["Land/0.png","Land/1.png","Land/2.png"],
"Skill": ["Skill/0.png","Skill/1.png","Skill/2.png","Skill/3.png","Skill/4.png","Skill/5.png"],
"Skill2": ["Skill2/0.png","Skill2/1.png","Skill2/2.png","Skill2/3.png","Skill2/4.png"],
"Stoned": ["Stoned/0.png","Stoned/1.png"],
"Walk": ["Walk/0.png","Walk/1.png","Walk/2.png","Walk/3.png","Walk/4.png","Walk/5.png"]
},

It means that there should be folder structure

- Attack with frames 0.png, 1.png, 2.png
- Death .....

"Walk/4.png":
{
"frame": {"x":32,"y":128,"w":32,"h":32},
"rotated": false,
"trimmed": false,
"spriteSourceSize": {"x":0,"y":0,"w":32,"h":32},
"sourceSize": {"w":32,"h":32},
"anchor": {"x":0.5,"y":0.42}
},
each frame has defined Frame size and where it is exactly placed, ignore anchor. You need to read Spritesheet.png find exact frame.

In case Animations are not defined, then everything is in output file without folder structure. Animations define folder structure

Spritesheet.json describes each frame, where it is placed and what size it has, folder structure

Acceptance Criteria:

- Able to read spritesheet json and png
- Split spritesheet into separate frames based on "frame" x,y and width/height
- create folder structure based on animations

Goals:
We want to run script to separate spritesheet into frame by frame folder structure.

Additional Option:
We want to make also automatic resize to 64x64 baseline, so frame let's say is 32x32, we create 64x64 and place the frame in the center, but does not RESIZE. so we just add empty space to all 4 directions to make it 64x64. This should be as an option e.g. -fs=64 (set to 64x64)
