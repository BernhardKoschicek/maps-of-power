from setuptools import setup

package_json = {
    "dependencies": {
        "bootstrap-autocomplete": "2.3.7",
        "bootstrap": "^5.1.3",
        "baguettebox.js": "1.11.1"
    }
}

setup(
    name='mapsofpower',
    setup_requires=['calmjs', 'libsass >= 0.6.0'],
    sass_manifests={
        'mop': ('static/sass', 'static/css', '/static/css')},
    package_json=package_json
)
