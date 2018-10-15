import imp
import os
import subprocess
backupmanager=imp.load_source("BackupManager","/usr/share/n4d/python-plugins/support/BackupManager.py")

class PmbManager:
	
	def __init__(self):
		self.pmb=backupmanager.BackupManager(app='pmb')
		pmbFiles={} 
		pmbDbFiles={'pmb':['/etc/pmb/debian-db.php']} 

		self.pmb.set_app_files(pmbFiles)
		self.pmb.set_app_dbFiles(pmbDbFiles) 

	def restore(self,file_path=None):
		self.pmb.set_backup_name("PmbManager")
		retVal=self.pmb.restore(file_path)
		self.change_pmb_version()
		return retVal


	def backup(self,dir='/backup'):
		self.pmb.set_backup_name(get_backup_name("PmbManager"))
		retVal=self.pmb.backup(dir)
		self.last_operations()
		return retVal

	def last_operations(self):
		#Regenerate cnames 
		cmd="lliurex-pmb --hosts"
		return (os.system(cmd))
		
	def change_pmb_version(self):

		mysql_command='mysql -uroot -p$(sudo mysql_root_passwd -g) -e '
		#Get bdd_version value frothom parametres table
		sql='"select valeur_param from pmb.parametres where type_param=\'pmb\' and sstype_param=\'bdd_version\'"'
		cmd=mysql_command + sql
		p=subprocess.check_output(cmd,shell=True)
		version=p.split("\n")[1]
		
		if version=="v4.47":
			sql='"update pmb.parametres set valeur_param=\'vLlxNemo\' where type_param=\'pmb\' and sstype_param=\'bdd_version\'"'
			cmd=mysql_command + sql
			os.system(cmd)
		elif version=="v5.10":
			sql='"update pmb.parametres set valeur_param=\'vLlxPandora\' where type_param=\'pmb\' and sstype_param=\'bdd_version\'"'
			cmd=mysql_command + sql
			os.system(cmd)
	
		elif version=="v5.14":
			sql='"update pmb.parametres set valeur_param=\'vLlxTrusty\' where type_param=\'pmb\' and sstype_param=\'bdd_version\'"'
			cmd=mysql_command + sql
			os.system(cmd)			
