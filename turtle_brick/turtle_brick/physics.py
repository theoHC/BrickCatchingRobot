class World:
    """Keep track of the physics of the world."""

    def __init__(self, brick, gravity, radius, dt):
        """
        Initialize the world.

        Args:
        brick - The (x,y,z) location of the brick
        gravity - the acceleration due to gravity in m/s^2
        radius - the radius of the platform
        dt - timestep in seconds of the physics simulation
        """

        self.brick_loc=brick
        self.brick_vel=(0.0,0.0,0.0)
        self.gravity=gravity
        self.radius=radius
        self.dt=dt

    @property
    def brick(self):
        """
        Get the brick's location.

        Return:
            (x,y,z) location of the brick
        """
        return self.brick_loc

    @brick.setter
    def brick(self, location):
        """
        Set the brick's location.

        Args:
           location - the (x,y,z) location of the brick
        """
        self.brick_loc = location
        self.brick_vel = (0.0,0.0,0.0)

    def drop(self):
        """
        Update the brick's location by having it fall in gravity for one timestep
        """
        self.brick_vel = (self.brick_vel[0],
                          self.brick_vel[1],
                          self.brick_vel[2] - self.gravity*self.dt)
        
        self.brick_loc = (self.brick_loc[0] + self.brick_vel[0]*self.dt,
                          self.brick_loc[1] + self.brick_vel[1]*self.dt,
                          self.brick_loc[2] + self.brick_vel[2]*self.dt)
        
        if self.brick_loc[2] < 0.0:
            self.brick_loc = (self.brick_loc[0],
                              self.brick_loc[1],
                              0.0)
            self.brick_vel = (0.0,0.0,0.0)