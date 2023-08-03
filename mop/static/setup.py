from setuptools import setup

package_json = {
    "dependencies": {
        "baguettebox.js": "1.11.1",
        "bootstrap-autocomplete": "2.3.7",
        "bootstrap": "^5.1.3",
        "bootstrap-icons": "1.10.3",
        "datatables.net-bs5": "^1.13.4",
        "datatables.net-buttons-bs5": "^2.3.6",
        "datatables.net-responsive-bs5": "^2.4.1",
        "datatables.net-searchbuilder-bs5": "^1.4.2",
        "datatables.net-searchpanes-bs5": "^2.1.2",
        "jquery": "^3.6.0",
        "jquery-ui-dist": "^1.13.1",
        "muuri": "^0.9.5"
    }
}

setup(
    name='mapsofpower',
    setup_requires=['calmjs'],
    sass_manifests={
        'mop': ('static/sass', 'static/css', '/static/css')},
    package_json=package_json,
    py_modules=[]
)
