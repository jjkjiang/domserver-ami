#!/bin/bash
# Expects to find DOMSERVER_S3_FILE and DOMSERVER_S3_BUCKET in the env variables

INSTALLDIR="/srv/${DOMSERVER_S3_FILE%%.*}"
mkdir -p $INSTALLDIR

aws s3 cp s3://${DOMSERVER_S3_BUCKET}/${DOMSERVER_S3_FILE} /tmp/${DOMSERVER_S3_FILE}
tar zxf /tmp/${DOMSERVER_S3_FILE} -C "$INSTALLDIR"

# run script to install/post configuration
cd $INSTALLDIR
./setup.sh

# now we configure apache2, and reload it
cp $INSTALLDIR/apache2.conf /etc/apache2/sites-enabled/domserver.conf
service apache2 graceful
