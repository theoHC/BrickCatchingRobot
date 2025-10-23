import unittest

from turtle_brick import physics


class TestPhysics(unittest.TestCase):

    def test_init(self):
        phys = physics.World(brick=(0.0, 0.0, 10.0), gravity=9.81,
                             radius=1.0, dt=0.1, falling=True)

        self.assertEqual(phys.brick, (0.0, 0.0, 10.0))
        self.assertEqual(phys.gravity, 9.81)
        self.assertEqual(phys.radius, 1.0)
        self.assertEqual(phys.dt, .1)
        self.assertEqual(phys.falling, True)

    def test_brick_fall(self):
        # Initialize physics with a brick at height 10
        phys = physics.World(brick=(0.0, 0.0, 10.0), gravity=9.81,
                             radius=1.0, dt=0.1, falling=True)

        # Simulate falling for 1 second (10 timesteps)
        for _ in range(10):
            phys.drop()

        # Check that the brick is moving at approximately 9.81 m/s downward
        self.assertAlmostEqual(phys.brick_vel[2], -9.81, delta=.1)
        self.assertAlmostEqual(phys.brick_loc[2], 4.9, delta=.5)

        for _ in range(20):
            phys.drop()

        self.assertEqual(phys.brick_vel[2], 0.0)
        self.assertEqual(phys.brick_loc[2], 0.0)

    def test_brick_setter(self):
        phys = physics.World(brick=(0.0, 0.0, 5.0), gravity=9.81,
                             radius=1.0, dt=0.1, falling=True)
        phys.brick = (1.0, 1.0, 2.0)
        self.assertEqual(phys.brick, (1.0, 1.0, 2.0))
        self.assertEqual(phys.brick_vel, (0.0, 0.0, 0.0))


if __name__ == '__main__':
    import rosunit
    rosunit.unitrun('turtle_brick', 'test_physics', TestPhysics)
