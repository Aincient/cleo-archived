rm docs/*.rst
rm -rf builddocs/
sphinx-apidoc src/muses --full -o docs -H 'Cleo' -A 'Goldmund, Wyldebeast & Wunderliebe <info@gw20e.com>' -V '0.1' -f -d 20
cp docs/conf.distrib docs/conf.py
