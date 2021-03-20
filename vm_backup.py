#!/usr/bin/python


from psphere.client import Client
from psphere.managedobjects import VirtualMachine, VirtualDiskManager, FileManager, Datacenter
from datetime import datetime, date, timedelta
import time, logging

# datastore name where to backup
BackupToDatastore="[backup]"
# how many days keep backups
KeepDays=1
client = Client("host","root","password")
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("esxibackup")
logging.getLogger("psphere").setLevel("WARN")

dclist=Datacenter.all(client)
dc=dclist[0]

vmlist = VirtualMachine.all(client)

vdm=client.sc.virtualDiskManager
fileManager=client.sc.fileManager


for vm in vmlist:
    logger.debug("Found vm: %s" %vm.name)
    logger.debug(vm.config.files.vmPathName)
    logger.debug(vm.config.datastoreUrl[0].url)
    logger.debug(vm.config.files.vmPathName)
    if vm.name in open('backup.list').read():
                logger.info("Found vm %s on backup list" %vm.name)
                destination=BackupToDatastore+" "+datetime.now().strftime("%Y-%m-%d")+"/"+vm.name
                fileManager.MakeDirectory(name=destination,
                        datacenter=dc,
                        createParentDirectories=True)
                task=fileManager.CopyDatastoreFile_Task(sourceName=vm.config.files.vmPathName,
                        sourceDatacenter=dc,
                        destinationName=destination+"/%s.vmx" %(vm.name),
                        destinationDatacenter=None,
                        force=True)
                logger.info("Creating virtual machine %s snapshot" %vm.name)
                task=vm.CreateSnapshot_Task(name="backup",
                                        description="Automatic backup "+datetime.now().strftime("%Y-%m-%d %H:%M:%s"),
                                        memory=False,
                                        quiesce=True)

                while task.info.state in ["queued", "running"]:
                        time.sleep(5)
                        task.update()
                logger.info("Snapshot created")
                snapshot=task.info.result

                for device in vm.config.hardware.device:
                        if device.__class__.__name__ == 'VirtualDisk':
                                logger.info("Backuping %s to %s" %(device.backing.fileName,destination))
                                dstSpec = client.create("VirtualDiskSpec")
                                dstSpec.adapterType="pvscsi"
                                dstSpec.diskType="thin"
                                task=vdm.CopyVirtualDisk_Task(sourceName=device.backing.fileName,
                                                                                  sourceDatacenter=dc,
                                                                                  destName=destination+"/"+device.backing.fileName.rsplit('/')[1],
                                                                                  destDatacenter=None,
                                                                                  destSpec=None,
                                                                                  force=False)
                                while task.info.state in ["queued", "running"]:
                                        time.sleep(5)
                                        task.update()
                                        logger.debug("task update")
                                if task.info.state == "success":
                                        elapsed_time = task.info.completeTime - task.info.startTime
                                        logger.info("Elapsed time: %s" %elapsed_time)
                                elif task.info.state == "error":
                                        logger.error("ERROR: The task finished with an error. If an error was reported it will follow.")
                                        try:
                                                logger.error("ERROR: %s" % task.info.error.localizedMessage)
                                        except AttributeError:
                                                logger.error("ERROR: There is no error message available.")
                                else:
                                        logger.error("UNKNOWN: The task reports an unknown state %s" % task.info.state)

                logger.info("Removing virtual machine %s snapshot" %vm.name)
                task=snapshot.RemoveSnapshot_Task(removeChildren=True)
                while task.info.state in ["queued", "running"]:
                        time.sleep(5)
                        task.update()
                        logger.debug("task update")


for ds in dc.datastore:
        if ds.name==BackupToDatastore[1:-1]:
                task=ds.browser.SearchDatastore_Task(datastorePath=BackupToDatastore)
                while task.info.state in ["queued", "running"]:
                        time.sleep(1)
                        task.update()
                if task.info.state == "success":
                        for file in task.info.result.file:
                                try:
                                        backup_date=datetime.strptime(file.path,"%Y-%m-%d")
                                        from_date = date.today()-timedelta(days=KeepDays)
                                        if backup_date.date() < from_date:
                                                logger.info("Deleting old backup %s" %file.path)
                                                delete_task=fileManager.DeleteDatastoreFile_Task(name=BackupToDatastore+"/"+file.path,datacenter=dc)
                                                while delete_task.info.state in ["queued", "running"]:
                                                        time.sleep(1)
                                                        delete_task.update()
                                except ValueError:
                                        logger.info("Ignoring folder '%s'" %file.path)


