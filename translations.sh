pybabel extract -F mop/translations/babel.cfg -k _l -o mop/translations/messages.pot .
pybabel update -i mop/translations/messages.pot -d mop/translations
