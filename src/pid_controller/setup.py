from setuptools import find_packages, setup

package_name = 'pid_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/launch.py'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='fezaro',
    maintainer_email='fezaro@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'pid_controller_node = pid_controller.pid_controller_node:main',
            'reference_input_node = pid_controller.reference_input_node:main',
        ],
    },
)
