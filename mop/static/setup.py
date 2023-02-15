from setuptools import setup

package_json = {
    "dependencies": {
        "bootstrap-autocomplete": "2.3.7",
        "bootstrap": "^5.1.3",
    }
}

setup(
    name='mapsofpower',
    setup_requires=['calmjs'],
    package_json=package_json
)
