#!/bin/bash -ex
# Expects to find DOMSERVER_S3_BUCKET, DOMSERVER_S3_REGION, DOMSERVER_S3_FILE in the env variables

INSTALLDIR="/srv/${DOMSERVER_S3_FILE%%.*}"
mkdir -p $INSTALLDIR

aws s3 cp --region=${DOMSERVER_S3_REGION} s3://${DOMSERVER_S3_BUCKET}/${DOMSERVER_S3_FILE} /tmp/${DOMSERVER_S3_FILE}
tar zxf --no-same-owner -/tmp/${DOMSERVER_S3_FILE} -C "$INSTALLDIR"

# run script to install/post configuration
cd $INSTALLDIR
chmod +x $INSTALLDIR/setup.sh
./setup.sh

# now we configure apache2, and reload it
cp $INSTALLDIR/apache2.conf /etc/apache2/sites-enabled/domserver.conf
service apache2 graceful
