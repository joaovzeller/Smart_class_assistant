from setuptools import setup
import os
from glob import glob

package_name = 'classroom_automation'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name] if os.path.exists('resource/' + package_name) else []),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'click'],
    zip_safe=True,
    maintainer='Member 5',
    maintainer_email='member5@example.com',
    description='Smart Classroom Audio and Servo Tracking System',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'audio_processing_node = classroom_automation.audio_processing_node:main',
            'servo_controller_node = classroom_automation.servo_controller_node:main',
        ],
    },
)