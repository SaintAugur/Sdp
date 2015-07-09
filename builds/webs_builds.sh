#!/bin/bash
#boot web services.
source $SDP_HOME/global.func
[ -z $init_user ] && ERROR
[ -z $init_user_dns ] && ERROR
[ -z $init_service_type ] && ERROR

container_nginx=staugur/nginx
container_httpd=staugur/httpd
container_tomcat=staugur/tomcat

#Ask:/data include wwwroot,logs.
case $init_service_type in
nginx)
  container_id=`docker run -tdi --name $init_user -v ${init_user_home_root}:/data/wwwroot/html $container_nginx`
  ;;
httpd)
  container_id=`docker run -tdi --name $init_user -v ${init_user_home_root}:/data/wwwroot/html $container_httpd`
  ;;
tomcat)
  container_id=`docker run -tdi --name $init_user -v ${init_user_home_root}:/data/wwwroot/html $container_tomcat`
  ;;
*)
  echo -e "\033[31mUnsupported service type！\033[0m"
  ERROR
  dockererror
  ;;
esac

container_ip=$(sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}' $init_user)
container_pid=$(sudo docker inspect --format '{{.State.Pid}}' $init_user)
echo "$container_ip  $init_user_host" >> /etc/hosts

case $init_service_type in
nginx)
  docker exec -ti $container_id /usr/sbin/nginx
  docker exec -ti $container_id /etc/init.d/php-fpm start
  ;;
httpd)
  docker exec -ti $container_id /etc/init.d/httpd start
  ;;
tomcat)
  echo
  ;;
*)
  exit 1
  ;;
esac

source $SDP_HOME/.end.sh
