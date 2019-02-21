echo 'Compiling messages for muses...'
cd src/muses/
django-admin.py compilemessages -l nl

echo 'Compiling messages for implementation server...'
cd ../../implementation/server/
django-admin.py compilemessages -l nl
