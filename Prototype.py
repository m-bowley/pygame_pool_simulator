import math
import time

WIDTH = 760
HEIGHT = 380

class Ball:
    def __init__(self, image, pos):
        self.actor = Actor(image, center=(pos[0], pos[1]), anchor=("center", "center"))
        self.movement = [0, 0]
        self.pocketed = False 
    
    def move(self):
        self.actor.x += self.movement[0]
        self.actor.y += self.movement[1]
        if self.pocketed == False:
            if self.actor.y < playArea.top + 16 or self.actor.y > playArea.bottom-16:
                self.movement[1] = -self.movement[1]
                self.actor.y = clamp(self.actor.y, playArea.top+16, playArea.bottom-16)
            if self.actor.x < playArea.left+16 or self.actor.x > playArea.right-16:
                self.movement[0] = -self.movement[0]
                self.actor.x = clamp(self.actor.x, playArea.left+16, playArea.right-16)      
        else:
            self.actor.x += self.movement[0]
            self.actor.y += self.movement[1]
    
    def resistance(self):
        # Slow the ball down
        self.movement[0] *= 0.95
        self.movement[1] *= 0.95

        if abs(self.movement[0]) + abs(self.movement[1]) < 0.4:
            self.movement = [0, 0]
        
    
    def collide(self, ball):
        collision_normal = [ball.actor.x - self.actor.x, ball.actor.y - self.actor.y]
        ball_speed = math.sqrt(collision_normal[0]**2 + collision_normal[1]**2)
        self_speed  = math.sqrt(self.momentum[0]**2 + self.momentum[1]**2)
        if self.momentum[0] == 0 and self.momentum[1] == 0:
            ball.momentum[0] = -ball.momentum[0]
            ball.momentum[1] = -ball.momentum[1]
        elif ball_speed > 0:
            collision_normal[0] *= 1/ball_speed
            collision_normal[1] *= 1/ball_speed
            ball.momentum[0] = collision_normal[0] * self_speed
            ball.momentum[1] = collision_normal[1] * self_speed
        
    
playArea = Actor("playarea.png", center=(WIDTH//2, HEIGHT//2))    
            
balls = []       
cue_ball = Ball("cue_ball.png", (WIDTH//2, HEIGHT//2))
balls.append(cue_ball)
balls.append(Ball("ball_1.png", (WIDTH//2 - 75, HEIGHT//2)))
balls.append(Ball("ball_2.png", (WIDTH//2 - 150, HEIGHT//2)))



pockets = []
pockets.append(Actor("pocket.png", topleft=(playArea.left, playArea.top), anchor=("left", "top")))
pockets.append(Actor("pocket.png", bottomleft=(playArea.left, playArea.bottom), anchor=("left", "bottom")))
pockets.append(Actor("pocket.png", bottomright=(playArea.right, playArea.bottom), anchor=("right", "bottom")))
pockets.append(Actor("pocket.png", topright=(playArea.right, playArea.top), anchor=("right", "top")))

shot_rotation = 270.0
turn_speed = 1
shot_line = []
max_line_length = 400
ball_speed = 30




held = False
held_time = 0.0
start_time = 0.0
hit_state = 0

hit_metre = Actor("hit_metre0.png", (0, 0), anchor=("center", "center"))

shot = False

def on_mouse_down(pos):
    global held, hit_state, start_time, held_time, hit_metre
    print("Clicked")
    if held == False:
        held = True
        start_time = time.time()
        hit_metre.pos = (cue_ball.actor.x + 50, cue_ball.actor.y - 50)
        hit_state = 0
        

def on_mouse_up():
    global held, shot, cue_ball, hit_state
    held = False
    shot = True

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))    
    

def update():
    global cue_ball, line, shot_rotation, hit_state, start_time, held_time, hit_metre, shot, balls
    
    ## Rotate your aim
    if keyboard[keys.LEFT] and not shot:
        shot_rotation -= 1 * turn_speed
    if keyboard[keys.RIGHT] and not shot:
        shot_rotation += 1 * turn_speed

    # Make the rotation wrap around
    if shot_rotation > 360:
        shot_rotation -= 360
    if shot_rotation < 0:
        shot_rotation += 360

    ## Shoot the ball with the space bar
    if keyboard[keys.SPACE] and not shot:
        shot_rotation += 1 * turn_speed

    # Work out the Vector that corresponds to the rotation
    rot_rads = current_rot * (math.pi/180) 

    x = math.sin(rot_rads)
    y = -math.cos(rot_rads)
    
    # Shoot the ball and move all the balls on the table
    if shot:
        shot = False
        balls_pocketed = []
        collisions = []
        for b in range(len(balls)):
            # Move each ball
            balls[b].move()
            # Check for collisions
            for other in balls:
                if balls.index(other) != b and balls[b].actor.colliderect(other.actor):
                    collisions.append((balls[b], other)) 
            if abs(balls[b].momentum[0]) + abs(balls[b].momentum[1]) > 0.4:
                shot = True
            else:
                balls[b].momentum = [0, 0]
            # Did it sink in the hole?
            in_pocket = balls[b].actor.collidelistall(pockets)
            if len(in_pocket) > 0 and balls[b].pocketed == False:
                if balls[b] != cue_ball:
                    balls[b].momentum[0] = (pockets[in_pocket[0]].x - balls[b].actor.x) / 20
                    balls[b].momentum[1] = (pockets[in_pocket[0]].y - balls[b].actor.y) / 20
                    balls[b].pocket = pockets[in_pocket[0]]
                    balls_pocketed.append(balls[b])
                else:
                    balls[b].x = WIDTH//2
                    balls[b].y = HEIGHT//2
        for col in collisions:
            col[0].collide(col[1])
        if shot == False:
            for b in balls_pocketed:
                balls.remove(b)

    else:
        cue_ball.momentum = [x*6*hit_state, y*6*hit_state]
        current_x = cue_ball.actor.x
        current_y = cue_ball.actor.y 
        length = 0
        line = []
        while length < max_line_length:
            hit = False
            if current_y < playArea.top or current_y > playArea.bottom:
                y = -y
                hit = True
            if current_x < playArea.left or current_x > playArea.right:
                x = -x
                hit = True
            if hit == True:
                line.append((current_x-(x*line_gap), current_y-(y*line_gap)))
            length += math.sqrt(((x*line_gap)**2)+((y*line_gap)**2) )
            current_x += x*line_gap
            current_y += y*line_gap
        line.append((current_x-(x*line_gap), current_y-(y*line_gap)))

def draw():
    global line
    screen.blit('table.png', (0, 0))
    playArea.draw()
    if not shot:
        screen.draw.line(cue_ball.actor.pos, line[0], (255, 255, 255))
        for l in range(len(line) - 1):
            screen.draw.line(line[l], line[l+1], (255, 255, 255))
    for ball in balls:
        if ball.pocketed == False:
            ball.actor.draw()
    if held:
        hit_metre.draw()
