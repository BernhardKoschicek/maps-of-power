from setuptools import setup

package_json = {
    "dependencies": {
        "@fortawesome/fontawesome-free": "^5.15.4",
        "baguettebox.js": "1.11.1",
        "bootstrap-autocomplete": "2.3.7",
        "bootstrap": "^5.1.3",
        "bootstrap-icons": "1.10.3",
        "datatables.net-buttons-dt": "^1.7.1",
        "datatables.net-buttons": "^1.7.1",
        "datatables.net-dt": "^1.11.5",
        "datatables.net": "^1.11.5",
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
