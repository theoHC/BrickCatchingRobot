from setuptools import find_packages, setup

package_name = 'turtle_brick'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml',
                                   'launch/show_turtle.launch.xml',
                                   'launch/run_turtle.launch.xml',
                                   'urdf/turtle_bot.urdf.xacro',
                                   'urdf/turtle_bot.urdf',
                                   'urdf/usefulstuff.xacro',
                                   'config/peruse_turtle.rviz',
                                   'config/run_turtle.rviz',
                                   'config/turtle.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='theoHC',
    maintainer_email='theo_coulson@me.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'arena = turtle_brick.arena:main',
            'turtlebot = turtle_brick.turtle_robot:main'
        ],
    },
)
