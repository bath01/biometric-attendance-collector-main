if [ -d migrations ]; then 
    flask db stamp head
else 
    flask db init
fi
flask db migrate && 
flask db upgrade &&
python3 app.py
