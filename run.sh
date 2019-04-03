wrkdir=`pwd`
u="$username"
p="$password"
t="$tenant"
docker run -itd -p 5000:80 \
           -e username="$u" \
           -e password="$p" \
           -e tenant="$t" \
            --volume=${wrkdir}/prj:/app flaskdock
