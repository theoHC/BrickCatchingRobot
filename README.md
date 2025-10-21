#MECH450 Homework 2

Author: Theo Coulson

Uses the turtlesim as the basis for simulating a robot which can catch a falling brick upon its platform, and carry it to the center of the arena before tipping it unceremoniously into oblivion.

## Quickstart
1. Use `ros2 launch turtle_brick run_turtle.launch.xml` to start the arena and turtle simulation.

2. Use `ros2 service call /place turtle_brick_interfaces/srv/Place 'point: {x: 2.0, y: 2.0, z: 16.0}'` to place the brick in an appropriate location

3. Use  `ros2 service call /drop std_srvs/srv/Empty` to drop the brick

4. Here's a video of a successful catch:

https://github.com/user-attachments/assets/62d45864-6766-446f-9ee3-382832486007

5. Here's a video of a failed catch:

https://github.com/user-attachments/assets/fc3c5fb9-e00c-44f8-9750-3f2e818b9b5a