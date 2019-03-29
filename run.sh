wrkdir=`pwd`
docker run -p 5000:80 --volume=${wrkdir}/prj:/app flaskdock
