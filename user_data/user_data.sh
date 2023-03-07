#!/bin/bash
TOMCAT_URL="https://downloads.apache.org/tomcat/tomcat-8/v8.5.86/bin/apache-tomcat-8.5.86.tar.gz"

function checkJavaHome {
    if [ -z ${JAVA_HOME} ]
    then
        sudo amazon-linux-extras install -y java-openjdk11
        export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
        export PATH=$PATH:$JAVA_HOME/bin
    else
        echo 'JAVA_HOME found: '$JAVA_HOME
    fi
}
#Check JAVA_HOME and install java
checkJavaHome

#Download tomcat
if [ ! -f /etc/apache-tomcat-8*tar.gz ]
then
    sudo curl -O --output-dir /etc $TOMCAT_URL
fi

sudo mkdir -p '/opt/tomcat/8_5'
if [ -d "/opt/tomcat/8_5" ]
then
    #uncompress apache-tomcat*.tar.gz
    cd /etc
    sudo tar xzf apache-tomcat-8.5.86.tar.gz -C "/opt/tomcat/8_5" --strip-components=1
    sudo groupadd tomcat
    sudo useradd -s /bin/false -g tomcat -d /opt/tomcat tomcat

    #Generate key ssl
    $JAVA_HOME/bin/keytool -genkey -alias tomcat -keyalg RSA -keystore /.keystore -dname "CN=lehoai, OU=sbifpt, O=sbifpt, L=danang, S=vietnam, C=vn" -storepass sbifpt123456 -keypass sbifpt123456

    #Get source code from s3 bucket to tomat
    sudo yum install unzip
    cd "/opt/tomcat/8_5/webapps"
    sudo mkdir sbi
    cd "sbi"
    aws s3 cp s3://tomcat-simple-web/index.zip .
    unzip -o index.zip

    cd "/opt/tomcat/8_5"

    # Config tomcat https
    sudo sed -i~ '/<Service name="Catalina"/a <Connector protocol="org.apache.coyote.http11.Http11NioProtocol" port="8443" maxThreads="200" scheme="https" secure="true" SSLEnabled="true" keystoreFile="/.keystore" keystorePass="sbifpt123456" clientAuth="false" sslProtocol="TLS"/>' conf/server.xml
    sudo sed -i~ '/<Service name="Catalina"/a <Connector scheme="https" secure="true" proxyPort="443" port="8080" protocol="HTTP/1.1" connectionTimeout="25000" URIEncoding="UTF-8" redirectPort="8443" />' conf/server.xml

    #Set default webapps
    sudo sed -i~ '/unpackWARs="true" autoDeploy="true">/a <Context path="" docBase="/opt/tomcat/8_5/webapps/sbi"> <WatchedResource>WEB-INF/web.xml</WatchedResource> </Context>' conf/server.xml
    
    #Set permisstion for tomcat config
    sudo chgrp -R tomcat "/opt/tomcat/8_5"
    sudo chmod -R g+r conf
    sudo chmod -R g+x conf
    sudo chmod -R g+w conf
    sudo chown -R tomcat webapps/ work/ temp/ logs/

    sudo touch tomcat.service
    sudo chmod 777 tomcat.service
    echo "[Unit]" > tomcat.service
    echo "Description=Apache Tomcat Web Application" >> tomcat.service
    echo "After=network.target" >> tomcat.service
    echo "[Service]" >> tomcat.service
    echo "Type=forking" >> tomcat.service

    #Set environment for tomcat
    echo "Environment=JAVA_HOME=$JAVA_HOME" >> tomcat.service
    echo "Environment=CATALINA_PID=/opt/tomcat/8_5/temp/tomcat.pid" >> tomcat.service
    echo "Environment=CATALINA_HOME=/opt/tomcat/8_5" >> tomcat.service
    echo "Environment=CATALINA_BASE=/opt/tomcat/8_5" >> tomcat.service
    echo "Environment=CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC" >> tomcat.service
    echo "Environment=JAVA_OPTS=-Djava.awt.headless=true -Djava.security.egd=file:/dev/./urandom" >> tomcat.service

    echo "ExecStart=/opt/tomcat/8_5/bin/startup.sh" >> tomcat.service
    echo "ExecStop=/opt/tomcat/8_5/bin/shutdown.sh" >> tomcat.service

    echo "User=tomcat" >> tomcat.service
    echo "Group=tomcat" >> tomcat.service
    echo "UMask=0007" >> tomcat.service
    echo "RestartSec=10" >> tomcat.service
    echo "Restart=always" >> tomcat.service

    echo "[Install]" >> tomcat.service
    echo "WantedBy=multi-user.target" >> tomcat.service

    sudo mv tomcat.service /etc/systemd/system/tomcat.service
    sudo chmod 755 /etc/systemd/system/tomcat.service

    #start tomcat service
    sudo systemctl daemon-reload
    sudo systemctl start tomcat
    exit
else
    exit
fi

