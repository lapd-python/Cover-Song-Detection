# Cover-Song-Detection
Using dft-fingerprinting and k-nn to determine which song the input is a cover of
```sh
docker rm -f coverid
docker run -itd --name coverid \
    -v "$PWD":/usr/src/myapp \
    -w /usr/src/myapp \
    python:3.5

docker exec -it coverid bash

cat > requirements.txt << EOL
librosa
EOL
pip install -r requirements.txt
# Create DB
python create_database.py

# Check
python alpha.py
```
