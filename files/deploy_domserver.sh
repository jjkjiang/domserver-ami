#!/bin/bash -ex
# Expects to find DOMSERVER_S3_BUCKET, DOMSERVER_S3_REGION, DOMSERVER_S3_FILE in the env variables

# Special case the filename "latest" and assume it's a link to the latest file
if [ ${DOMSERVER_S3_FILE} == "latest" ]; then
  aws s3 cp --region=${DOMSERVER_S3_REGION} s3://${DOMSERVER_S3_BUCKET}/${DOMSERVER_S3_FILE} /tmp/domserver-latest-version
  DOMSERVER_S3_FILE=$(cat /tmp/domserver-latest-version)
fi

INSTALLDIR="/srv/${DOMSERVER_S3_FILE%%.*}"
mkdir -p $INSTALLDIR

aws s3 cp --region=${DOMSERVER_S3_REGION} s3://${DOMSERVER_S3_BUCKET}/${DOMSERVER_S3_FILE} "/tmp/${DOMSERVER_S3_FILE}"
tar --no-same-owner -zxf /tmp/${DOMSERVER_S3_FILE} -C "$INSTALLDIR"
rm "/tmp/${DOMSERVER_S3_FILE}"

# run script to install/post configuration
cd $INSTALLDIR
chmod +x $INSTALLDIR/setup.sh
./setup.sh

# now we configure nginx, and reload it
cp $INSTALLDIR/nginx-site.conf /etc/nginx/sites-enabled/domserver
cp $INSTALLDIR/php-fpm-pool.conf /etc/php5/fpm/pool.d/domserver.conf
service php5-fpm restart
service nginx restart
