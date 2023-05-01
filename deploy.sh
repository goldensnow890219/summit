source ./venv/bin/activate
export $(grep -v '^#' .env | xargs)
cd ./summit-0003 || exit 1
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
cd ..
chown www-data:www-data summit-0003 -R
ln -nsf summit-0003 summit && systemctl restart gunicorn
