IMAGE="evergiven.ury.york.ac.uk:5000/vase"
CONTAINER="vase"
PROJECTDIR="/opt/vase"
LOGDIR="/mnt/logs/"
PORT=5040
DATE=$(date +%s)

docker build -t $IMAGE:$DATE .
docker push $IMAGE:$DATE
docker service update --image $IMAGE:$DATE vase
