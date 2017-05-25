import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):
    num_frames = 0
    basename = ''
    varyC = 0

    for command in commands:
        if command[0]=='frames':
            num_frames=int(command[1])

        elif command[0]=="basename":
            basename=command[1]

        elif command[0]=="vary":
            varyC+=1

    if (varyC>0 and num_frames==0):
        print "used vary, no frames set"
        return

    if (num_frames>0 and basename==''):
        basename='default'
    return num_frames, basename

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    knobs=[dict() for x in range(num_frames)]
    for command in commands:
        if command[0]=='vary':
            for frame in range(num_frames):
                if frame in range(int(command[2]),int(command[3])+1):
                    if(frame==int(command[2])):
                        knobs[frame][command[1]]=float(command[4])
                    else:
                        knobs[frame][command[1]]=knobs[frame-1][command[1]]+((float(command[5])-float(command[4]))/(float(command[3])-float(command[2])))
    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    i=0
    
    num_frames, basename=first_pass(commands)
    print basename
    knob=second_pass(commands, num_frames)
    while i<num_frames:
        print i
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        tmp = []
        step = 0.1
        for command in commands:
            #print command
            c = command[0]
            args = command[1:]
            
            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                if args[3] != None:
                    #print "move: " + args[3] + " " + knob[frame][args[3]]
                    x = args[0]*knob[i][args[3]];
                    y = args[1]*knob[i][args[3]];
                    z = args[2]*knob[i][args[3]];
                    args = [x, y, z]
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if args[3] != None:
                    #print "scale: " + args[3] + " " + str(knob[frame][args[3]])
                    x = args[0]*knob[i][args[3]];
                    y = args[1]*knob[i][args[3]];
                    z = args[2]*knob[i][args[3]];
                    args = [x, y, z]
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                #print tmp;
                stack[-1] = [x[:] for x in tmp]
                #print stack[-1]
                tmp = []
            elif c == 'rotate':
                if args[2] != None:
                    #print "rotate: " + args[2] + " " + str(knob[frame][args[2]])
                    angle = args[1] * knob[i][args[2]];
                    args = [args[0], angle]
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                #print stack[-1];
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])

                
        if(x==0):
            save_extension(screen, "anim/"+basename+"000.png")            
        else:
            save_extension(screen, "anim/"+basename+("%03d"%i)+".png")

        i+=1

