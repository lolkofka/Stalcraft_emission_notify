docker container stop stalemiss
docker container rm stalemiss
docker image rm stalemissi
docker build -t stalemissi .
docker run -d --mount type=bind,source="$PWD"/data,target=/usr/app/data --restart unless-stopped --name stalemiss stalemissi
docker container ls