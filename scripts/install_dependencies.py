import os

try:
    import cmlapi
except ModuleNotFoundError:
    cluster = os.getenv("CDSW_API_URL")[:-1] + "2"
    !pip3 install {cluster}/python.tar.gz

!pip3 install -r requirements.txt 
