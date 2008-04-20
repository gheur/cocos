#
# An example of how to generate a 3D scene using Cocos
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from pyglet.gl import *
import cocos
from cocos.director import director
from cocos.euclid import Point2,Point3
import math


class Flag3D( cocos.layer.Layer ):

    def __init__( self ):

        super(Flag3D,self).__init__()

        # load the image
        self.image = pyglet.resource.image('flag.png')

        # get the texture
        self.texture = self.image.get_texture()

        # get image size
        x,y = self.image.width, self.image.height

        # size of the grid: 20 x 20
        # The image will be slipted in 20 squares x 20 tiles
        self.grid = Point2(20,20)

        # size of each tile
        self.x_step = x / self.grid.x
        self.y_step = y / self.grid.y

        # calculate vertex, textures depending on image size
        idx_pts, ver_pts_idx, tex_pts_idx = self._calculate_vertex_points()

        # Generates an indexed vertex array with texture, vertex and color
        # http://www.glprogramming.com/red/chapter02.html#name6
        self.vertex_list = pyglet.graphics.vertex_list_indexed( (self.grid.x+1) * (self.grid.y+1), 
                            idx_pts, "t3f", "v3f/stream","c4B")
        self.vertex_list.vertices = ver_pts_idx     # vertex points
        self.vertex_list.tex_coords = tex_pts_idx   # texels
        self.vertex_list.colors = (255,255,255,255) * (self.grid.x+1) * (self.grid.y+1) # colors 

        # hook on resize to override the 2D projection with a 3D projection
        director.push_handlers(self.on_resize)


    def on_enter(self):
        # the layer is on "stage"
        self.elapsed = 0

        # call the "step" method every frame
        self.enable_step()


    def on_resize( self, width, height ):
        # change the 2D projection to 3D
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(90, 1.0*width/height, 0.1, 400.0)
        glMatrixMode(GL_MODELVIEW)

        glShadeModel(GL_SMOOTH)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    def draw( self ):
        glLoadIdentity()

        # center the image
        glTranslatef(-320, -240, -320.0)

        # enable texture
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)

        # draw the vertex array
        self.vertex_list.draw(GL_TRIANGLES)

        # disable the texture
        glDisable(self.texture.target)


    def step( self, dt ):

        # move the z vertices with the sin(x+y) function
        # to simulate a 3D flag effect

        self.elapsed += dt
        amplitud = 32
        for i in range(0, self.grid.x+1):
            for j in range(0, self.grid.y+1):
                x,y,z = self.get_vertex(i,j)
                z = (math.sin(self.elapsed*math.pi*2 + (y+x) * .01) * amplitud)
                self.set_vertex( i,j, (x, y, z) )


    def _calculate_vertex_points(self):        
        # generate the vertex array with the correct values

        # size of the texture (power of 2)
        w = float(self.image.width)/self.texture.tex_coords[3]
        h = float(self.image.height)/self.texture.tex_coords[7]

        index_points = []
        vertex_points_idx = []
        texture_points_idx = []

        # generate 2 empty lists:
        #  vertex_list:
        #  texex_list:
        for x in range(0,self.grid.x+1):
            for y in range(0,self.grid.y+1):
                vertex_points_idx += [-1,-1,-1]
                texture_points_idx += [-1,-1,-1]

        # since we are using vertex_list_indexed we must calculate
        # the index points
        for x in range(0, self.grid.x):
            for y in range(0, self.grid.y):
                x1 = x * self.x_step 
                x2 = x1 + self.x_step
                y1 = y * self.y_step
                y2 = y1 + self.y_step
              
                #  d <-- c
                #        ^
                #        |
                #  a --> b 
                a = x * (self.grid.y+1) + y
                b = (x+1) * (self.grid.y+1) + y
                c = (x+1) * (self.grid.y+1) + (y+1)
                d = x * (self.grid.y+1) + (y+1)

                # we are generating 2 triangles: a-b-d, b-c-d
                # (and not 1 quad, to prevent concave quads
                # although this example can work OK with quads)
                index_points += [ a, b, d, b, c, d]

                l1 = ( a*3, b*3, c*3, d*3 )
                l2 = ( Point3(x1,y1,0), Point3(x2,y1,0), Point3(x2,y2,0), Point3(x1,y2,0) )

                # populate the vertex_list and the textex_list
                for i in range( len(l1) ):
                    vertex_points_idx[ l1[i] ] = l2[i].x
                    vertex_points_idx[ l1[i] + 1 ] = l2[i].y
                    vertex_points_idx[ l1[i] + 2 ] = l2[i].z

                    texture_points_idx[ l1[i] ] = l2[i].x / w
                    texture_points_idx[ l1[i] + 1 ] = l2[i].y / h
                    texture_points_idx[ l1[i] + 2 ] = 0.0

        return ( index_points, vertex_points_idx, texture_points_idx )

    def set_vertex( self, x, y, v):
        '''Set a vertex point is a certain value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex
            `v` : (int, int, int)
                tuple value for the vertex
        '''
        idx = (x * (self.grid.y+1) + y) * 3
        self.vertex_list.vertices[idx] = v[0]
        self.vertex_list.vertices[idx+1] = v[1]
        self.vertex_list.vertices[idx+2] = v[2]

    def get_vertex( self, x, y):
        '''Get the current vertex point value

        :Parameters:
            `x` : int 
               x-vertex
            `y` : int
               y-vertex

        :rtype: (int,int,int)
        '''
        idx = (x * (self.grid.y+1) + y) * 3
        x = self.vertex_list.vertices[idx]
        y = self.vertex_list.vertices[idx+1]
        z = self.vertex_list.vertices[idx+2]
        return (x,y,z)


if __name__ == '__main__':
    director.init()
    s = cocos.scene.Scene()
    s.add( Flag3D() )
    director.run( s )