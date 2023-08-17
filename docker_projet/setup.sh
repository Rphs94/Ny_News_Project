
docker-compose down
sudo rm finish.txt
sudo docker build -t raphadu94/etl:latest -f ~/docker_projet/ETL/image_etl/Dockerfile ~/docker_projet/
sudo docker build -t raphadu94/spark:latest -f ~/docker_projet/ETL/image_etl_spark/Dockerfile ~/docker_projet/
sudo docker build -t raphadu94/api:latest -f ~/docker_projet/api/Dockerfile ~/docker_projet/
sudo docker build -t raphadu94/dash:latest -f ~/docker_projet/dash/Dockerfile ~/docker_projet/
docker-compose up -d 