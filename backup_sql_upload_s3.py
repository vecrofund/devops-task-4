### SOURCES:
### https://docs.python.org/3/library/shutil.html#module-shutil
### http://boto.cloudhackers.com/en/latest/#
### backup_sql_upload_s3.py
### https://python-forum.io/Thread-Menu-selection-using-function

import os
import shutil
import boto
import datetime
import string
import tarfile
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from datetime import timedelta
from cryptography.fernet import Fernet

### variables:

### data/time variables
today = str(datetime.date.today())
now = datetime.datetime.now()

### connection info:
aws_secret_access_key = 'Secret Access-Key'
aws_access_key = 'Access Key'
aws_bucket_name = 'Bucket Name'
aws_folder_name = '/tmp/'

### MENU
def showmenu():
        print("\nBackup menu")
        print("---------------")
        print("A - Start backup")
        print("B - Remove backup")
        print("C - Status backup")
        print("Q - Exit\n")

def menu():
        while True:
            showmenu()
            choice = input("Enter your choice:")
            if choice == 'A':
                startBackup()
            elif choice == 'B':
                removeBackup()
            elif choice == 'C':
                statusBackup()
            elif choice == 'Q':
                return
            else:
                print("Try again")

if __name__ == '__main__':
    menu()

def startBackup():
        print(now + '- Backup is starting!')
### insert backup info:
        insert_backup_name = input ('Insert database name where you want to backup: ')
        backup_name = print(insert_backup_name + '.sql')
        insert_backup_dir = input ('Insert path to directory where you want to save backup: /tmp/...')
        backup_dir = print('/tmp/' +insert_backup_dir)

## backup info:
        backup_create_dir("mkdir" + backup_dir)
        backup_mysqldump= "mysqldump '"+ backup_name +"'  > '"+ backup_dir +"''"+ backup_name +"'"
        os.system(backup_create_dir)
        os.execute(backup_cmd)

### backup/archive variables:
        archieve_name = backup_name
        backup_path = backup_dir + backup_name
        archieve_path = backup_dir + archieve_name
        
### backuping/archiving:
        print(now + ' - Creating archive for ' + backup_name)
## shutil copying and removal functions
        shutil.make_archive(archieve_path, 'gztar', backup_dir)
        print(now + ' - Completed archiving database')
        full_archive_file_path = archieve_path + ".tar.gz"
        full_archive_name = archieve_name + ".tar.gz"

### Connect to S3
        s3 = S3Connection(aws_access_key, aws_secret_access_key)
        bucket_name = s3.get_bucket(aws_bucket_name)

### Upload backup to S3
        print(now + '- Uploading file archive ' + full_archive_name + '...')
        s3_bucket = Key(bucket_name)
        s3_bucket.key = aws_folder_name + full_archive_name
        print(s3_bucket.key)
        s3_bucket.set_contents_from_filename(full_archive_file_path)
        s3_bucket.set_acl("public-read")
        
        print(now + '- Clearing previous archives ' + full_archive_name + '...')
        shutil.rmtree(backup_dir)
        print(now + '- Removed backup of local database')
        print(now + '- Backup job is done')
        
def removeBackup():
        if os.path.exists(backup_dir + backup_name):
### removing backup file
                print("Removing backup file" + backup_dir + backup_name)
                os.remove(backup_dir + backup_name)
                print("Removed")
        else:
                print("The file does not exist!") 

def statusBackup():
        import os.path

        if os.path.isfile(backup_dir + backup_name):
           print ("Backup file" + backupdir + backup_name + " exists ")
        else:
            print ("File not exist")

      



       



