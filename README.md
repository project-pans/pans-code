# Central code repository for PANS 
The Pantry App Notification System (P.A.N.S.) utilizes a Raspberry Pi running a Django webserver, weight sensors, and a barcode scanner to keep track of a user's pantry inventory.
## MySQL Database
### Dependencies
- ```sudo apt install mysql-server```
- ```sudo update-rc.d mysql defaults```
### Configuration
- Copy the server configuration file ```my.cnf``` to ```/etc/mysql/my.cnf```
- ```sudo mysqladmin create pans_data```
- ```sudo mysql -u root```
  - ```USE pans_data;```
  - ```CREATE USER 'djangouser'@'%' IDENTIFIED WITH mysql_native_password BY 'password';```
  - ```GRANT ALL ON pans_data.* TO 'djangouser'@'%';```
  - ```FLUSH PRIVILEGES;```

## Web Server
### Dependencies
- ```sudo apt install python3-dev libmysqlclient-dev default-libmysqlclient-dev```
- ```sudo apt install python3-pip```
- ```pip3 install mysqlclient```
- ```sudo apt install python3-django```
- [Configure the MySQL database](#mysql-database)
### Usage
- Add SECRET_KEY to ```webserver/pans/pans/settings.py```
- ```cd webserver/pans```
- ```python3 manage.py runserver <IP_Address>:8000```
  - NOTE: The IP address used here must be specified in the ALLOWED_HOSTS section of ```webserver/pans/pans/settings.py```
### Dump MySQL Data
- NOTE: You must comment out the database line under ```[client]``` in ```/etc/mysql/my.cnf```
- ``` mysqldump --no-tablespaces -u djangouser -p pans_data | gzip > pans_data.gz```
### Importing MySQL Data
- [Configure the MySQL database](#mysql-database)
- ```gunzip < ~/pans-code/webserver/pans_data.gz | sudo mysql pans_data```

## Weight Sensors
- ```python3 weights_sql.py```

## Barcode Scanner
- ```python3 barcode.py```
