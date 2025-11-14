# 310-COSC

# to delete old coverage report and add a new one run the commands: 
rm -r htmlcov
coverage run -m pytest
coverage html

# to delete the old report folder and create a new one run the commands: 
rm -r report
pytest --junitxml=report/report.xml

#api website: http://127.0.0.1:8000/docs#/

To activate our virtual environment go to the fullproject then backend folder then enter: backendvenv\Scripts\Activate
To reload fastapi: uvicorn app.app:app --reload

pip list
Package           Version
----------------- ---------
annotated-types   0.7.0
anyio             4.11.0
bandit            1.8.6
certifi           2025.10.5
click             8.3.0
colorama          0.4.6
fastapi           0.119.1
h11               0.16.0
httpcore          1.0.9
httpx             0.28.1
idna              3.11
iniconfig         2.3.0
markdown-it-py    4.0.0
mdurl             0.1.2
packaging         25.0
passlib           1.7.4
pip               25.2
pluggy            1.6.0
pydantic          2.12.3
pydantic_core     2.41.4
Pygments          2.19.2
pytest            8.4.2
python-multipart  0.0.20
PyYAML            6.0.3
rich              14.2.0
sniffio           1.3.1
starlette         0.48.0
stevedore         5.5.0
typing_extensions 4.15.0
typing-inspection 0.4.2
uvicorn           0.38.0
