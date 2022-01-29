
import pygame, sys, time, random, json, math
from pygame.locals import *

pygame.init()
WIDTH, HEIGHT = 1000, 600
surface=pygame.display.set_mode((WIDTH, HEIGHT),0,32)
fps=64
ft=pygame.time.Clock()
pygame.display.set_caption("Shoot the Bird")

ARROW_SOURCE = (0, HEIGHT)
ARROW_LENGTH = 100

BIRD_IMAGE = pygame.image.load("src/Bird.png")

class Arrow:
    def __init__(self):
        self.dist = 0
        self.angle = random.randint(270, 360)
        self.speed = 7
    def move(self):
        self.dist += self.speed
    def get_pos(self):
        angle = math.radians(self.angle)
        x1 = ARROW_SOURCE[0]+((self.dist+ARROW_LENGTH)*math.cos(angle))
        y1 = ARROW_SOURCE[1]+((self.dist+ARROW_LENGTH)*math.sin(angle))
        x2 = ARROW_SOURCE[0]+(self.dist*math.cos(angle))
        y2 = ARROW_SOURCE[1]+(self.dist*math.sin(angle))
        front, rear = (x1, y1), (x2, y2)
        return front, rear

class Bird:
    def __init__(self):
        self.x_initial_offet = 1500
        self.pos = [1200, 200]
        self.speed = 3
        self.size = (80, 80)
        self.randomize()
        self.image = pygame.transform.scale(BIRD_IMAGE, self.size)
    def move(self):
        self.pos[0] -= self.speed
        if self.pos[0]<(0-self.size[0]):
            self.randomize()
    def randomize(self):
        self.pos = [random.randint(WIDTH, WIDTH+self.x_initial_offet), random.randint(0, HEIGHT-130-self.size[1])]


class App:
    def __init__(self, surface):
        self.surface = surface
        self.play = True
        self.mouse=pygame.mouse.get_pos()
        self.click=pygame.mouse.get_pressed()
        self.color = {
            "sky": (40, 140, 180),
            "grass": (40, 180, 80),
            "sea": (40, 80, 180),
            "bow": (120, 80, 40),
            "arrow": (120, 80, 40)
        }
        self.background = {
            "sea_level": 30,
            "grass_level": 100
        }
        self.bow_radius = 80
        self.bow_thickness = 6
        self.arrow_thickness = 3
        self.arrows = []
        self.last_shot_time = time.time()
        self.min_gap_between_shots = 0.3
        self.birds = []
        self.bird_count_range = list(range(4, 6))
        self.make_random_birds()
    def get_edge_points(self, bird):
        p1 = bird.pos[:]
        p2 = [bird.pos[0]+bird.size[0], bird.pos[1]]
        p3 = [bird.pos[0]+bird.size[0], bird.pos[1]+bird.size[1]]
        p4 = [bird.pos[0], bird.pos[1]+bird.size[1]]
        return [p1, p2, p3, p4]
    def does_arrow_hit_bird(self, arrow):
        for index in range(len(self.birds)):
            bird = self.birds[index]
            arrow_pos, _ = arrow.get_pos()
            min_bird_x = bird.pos[0]
            min_bird_y = bird.pos[1]
            max_bird_x = bird.pos[0]+bird.size[0]
            max_bird_y = bird.pos[1]+bird.size[1]
            if (min_bird_x<=arrow_pos[0]<=max_bird_x) and min_bird_y<=arrow_pos[1]<=max_bird_y:
                return index
        return None
    def make_random_birds(self):
        self.birds = []
        for _ in range(random.choice(self.bird_count_range)):
            new_bird = Bird()
            self.birds.append(new_bird)
    def draw_background(self):
        pygame.draw.rect(self.surface, self.color["sky"], (0, 0, WIDTH, HEIGHT-self.background["grass_level"]-self.background["sea_level"]))
        pygame.draw.rect(self.surface, self.color["sea"], (0, HEIGHT-self.background["grass_level"]-self.background["sea_level"], WIDTH, self.background["sea_level"]))
        pygame.draw.rect(self.surface, self.color["grass"], (0, HEIGHT-self.background["grass_level"], WIDTH, self.background["grass_level"]))
    def draw_bow_arrow(self):
        pygame.draw.circle(self.surface, self.color["bow"], ARROW_SOURCE, self.bow_radius, self.bow_thickness)
        for arrow in self.arrows:
            front, rear = arrow.get_pos()
            pygame.draw.line(self.surface, self.color["arrow"], front, rear, self.arrow_thickness)
    def draw_birds(self):
        for index in range(len(self.birds)):
            pos = self.birds[index].pos
            size = self.birds[index].size
            pygame.draw.rect(self.surface, self.color["arrow"], (pos[0], pos[1], size[0], size[1]), 1)
            self.surface.blit(self.birds[index].image, pos)
    def angle_between_three_points(self, p1, p2, p3):
        # p1 is the center
        P12 = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        P13 = math.sqrt((p1[0] - p3[0])**2 + (p1[1] - p3[1])**2)
        P23 = math.sqrt((p2[0] - p3[0])**2 + (p2[1] - p3[1])**2)
        angle = math.acos(((P12**2) + (P13**2) - (P23**2)) / (2 * P12 * P13))
        return angle
    def draw_default_arrow(self):
        angle = self.angle_between_three_points(ARROW_SOURCE, (WIDTH, HEIGHT), self.mouse)
        angle = math.radians(360-math.degrees(angle))
        target_x = ARROW_SOURCE[0]+(ARROW_LENGTH*math.cos(angle))
        target_y = ARROW_SOURCE[1]+(ARROW_LENGTH*math.sin(angle))
        pygame.draw.line(self.surface, self.color["arrow"], ARROW_SOURCE, (target_x, target_y), self.arrow_thickness)
    def shoot(self):
        if self.click[0]==1:
            if (time.time()-self.last_shot_time)>=self.min_gap_between_shots:
                angle = self.angle_between_three_points(ARROW_SOURCE, (WIDTH, HEIGHT), self.mouse)
                angle = 360-math.degrees(angle)
                new_arrow = Arrow()
                new_arrow.angle = angle
                self.arrows.append(new_arrow)
                self.last_shot_time = time.time()
    def move_arrows(self):
        for index in range(len(self.arrows)):
            self.arrows[index].move()
    def move_birds(self):
        for index in range(len(self.birds)):
            self.birds[index].move()
    def remove_wated_arrows(self):
        new_arrows_list = []
        for index in range(len(self.arrows)):
            front, rear  = self.arrows[index].get_pos()
            if (0<rear[0]<WIDTH) and (0<rear[1]<HEIGHT):
                new_arrows_list.append(self.arrows[index])
        self.arrows = new_arrows_list[:]
    def any_arrow_hit_birds(self):
        new_arrows = []
        for index in range(len(self.arrows)):
            bird_index = self.does_arrow_hit_bird(self.arrows[index])
            if bird_index is None:
                new_arrows.append(self.arrows[index])
            else:
                self.birds[bird_index].randomize()
        self.arrows = new_arrows[:]
    def action(self):
        self.shoot()
        self.move_arrows()
        self.move_birds()
        self.remove_wated_arrows()
        self.any_arrow_hit_birds()
    def render(self):
        self.draw_background()
        self.draw_birds()
        self.draw_bow_arrow()
        self.draw_default_arrow()
    def run(self):
        while self.play:
            self.surface.fill(self.color["sky"])
            self.mouse=pygame.mouse.get_pos()
            self.click=pygame.mouse.get_pressed()
            for event in pygame.event.get():
                if event.type==QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type==KEYDOWN:
                    if event.key==K_TAB:
                        self.play=False
                    if event.key==K_SPACE:
                        is_paused = True
                        while is_paused:
                            for event in pygame.event.get():
                                if event.type==QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if event.type==KEYDOWN:
                                    if event.key==K_TAB:
                                        self.play=False
                                    if event.key==K_SPACE:
                                        is_paused = False
            #--------------------------------------------------------------
            self.action()
            self.render()
            # -------------------------------------------------------------
            pygame.display.update()
            ft.tick(fps)



if  __name__ == "__main__":
    app = App(surface)
    app.run()

