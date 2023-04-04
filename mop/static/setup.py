from setuptools import setup

package_json = {
    "dependencies": {
        "baguettebox.js": "1.11.1",
        "bootstrap-autocomplete": "2.3.7",
        "bootstrap": "^5.1.3",
        "bootstrap-icons": "1.10.3",
        "masonry-layout": "4.2.2",
        "jquery": "^3.6.0",
        "jquery-ui-dist": "^1.13.1"
    }
}

setup(
    name='mapsofpower',
    setup_requires=['calmjs', 'libsass >= 0.6.0'],
    sass_manifests={
        'mop': ('static/sass', 'static/css', '/static/css')},
    package_json=package_json,
    py_modules=[]
)
