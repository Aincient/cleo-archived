echo 'Making messages for muses...'
cd src/muses/
django-admin.py makemessages -l nl

echo 'Making messages for implementation server...'
cd ../../implementation/server/
django-admin.py makemessages -l nl
