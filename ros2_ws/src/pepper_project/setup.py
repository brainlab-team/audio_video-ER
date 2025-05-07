from setuptools import find_packages, setup

package_name = 'pepper_project'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[  # Dati di configurazione per ROS 2
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
        'setuptools',
        'opencv-python',  # Necessario per OpenCV
        'fer',             # Necessario per il riconoscimento emozioni
        'cv-bridge',       # Necessario per convertire tra ROS Image e OpenCV
    ],
    zip_safe=True,
    maintainer='cais',
    maintainer_email='cais@todo.todo',
    description='Un pacchetto per gestire audio e immagini da Pepper',
    license='TODO: License declaration',  # Puoi aggiornare con la tua licenza
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'image_processor = pepper_project.image_processor:main',
            'pose_estimator = pepper_project.pose_estimator:main',
            'audio_processor = pepper_project.audio_processor:main',
            'audio_transcriber = pepper_project.audio_transcriber:main',
        ],
    },
)
