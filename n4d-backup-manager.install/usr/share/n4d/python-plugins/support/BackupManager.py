##################################################
#In order to add a backup:
# - Instatiate backupmanager class
# - Asign backup name, app files, dbfiles and dirs (if any)
# - For an example take a look to PmbManager or MoodleManager
##################################################

import tempfile
import shutil
import os
import subprocess
import tarfile
import time    

class BackupManager:
	def __init__(self,app=''):
		#Need to def files and dirs for moodle, pmb and others
		self.apps_files={}
		self.apps_dbFiles={} 
		self.apps_dirs={}
		self.db_configPath='/etc/lliurex-sgbd'
		self.backupName=''
		self.app=app
	
	def set_app_dbFiles(self,dbFiles):
		self.apps_dbFiles=dbFiles

	def set_app_files(self,files):
		self.apps_files=files

	def set_app_dirs(self,dirs):
		self.apps_dirs=dirs

	def set_backup_name(self,backupName=None):
		self.backupName=backupName
		return self.backupName

	def get_time(self):
		return self.backupName

	def get_db_name(self,app):
		try:
			files=os.listdir(self.db_configPath)
			dbName=''
			dbConfig=''
			for i in files:
				if app in i:
					dbConfig=i
					break
			if os.path.exists(self.db_configPath+'/'+dbConfig):
				for line in open(self.db_configPath+'/'+dbConfig):
					if line.startswith("DB_NAME"):
						dbName=str(line.split("=")[-1])
						dbName=dbName.rstrip()
						dbName=dbName.lstrip()
						break
				
                except Exception as e:
			print e
			return [False,str(e)]
		return dbName


	def backup(self,dir="/backup"):
		try:
			file_path=dir+"/"+self.get_time()
			tar=tarfile.open(file_path,"w:gz")
			if self.app in self.apps_files:
				for f in list(self.apps_files[self.app]):
					#Add file to tar
					if os.path.exists(f):
						tar.add(f)
			if self.app in self.apps_dirs:	
				for d in list(self.apps_dirs[self.app]):
					if os.path.exists(d):
					#Add dir to tar
						tar.add(d)
			if self.app in self.apps_dbFiles:
				dbDumpFile=self.dumpDb(str(self.app))
				if dbDumpFile!='':
					if os.path.exists(dbDumpFile):
							tar.add(dbDumpFile)
					else:
						print "%s database not found!!" % str(self.app)
				else:
					print "%s database not found!!" % str(self.app)

			tar.close()
			return [True,file_path]
                except Exception as e:
			print e
			return [False,str(e)]

	def restore(self,file_path=None):
		try:
			if file_path==None:
				for f in sorted(os.listdir("/backup"),reverse=True):
					if self.backupName in f:
						file_path="/backup/"+f
						break

			if file_path==None:
				return [False,"Backup file not found"]
			if os.path.exists(file_path):
				tmp_dir=tempfile.mkdtemp()
				tar=tarfile.open(file_path)
				tar.extractall(tmp_dir)
				tar.close()
				if self.app in self.apps_files:
					for f in list(self.apps_files[self.app]):
						tmp_path=tmp_dir+f
						#Avoid cname restore
						if not "/var/lib/dnsmasq/config/" in tmp_path:
							if os.path.exists(tmp_path):
								shutil.copy(tmp_path,f)
				
				if self.app in self.apps_dirs:
					for d in list(self.apps_dirs[self.app]):
						tmp_path=tmp_dir+d
						if os.path.exists(tmp_path):
#							self.mkdir(d)
							cmd="cp -r " + tmp_path + "/* " + d
							if not os.path.exists(d):
								os.makedirs(d)
							os.system(cmd)
	
				sw_updateDb=False
				if os.path.exists(tmp_dir+"/tmp"):
					for f in os.listdir(tmp_dir+"/tmp"):
						if ".sql" in f:
							self.restoreDb(tmp_dir+"/tmp/"+f)
							sw_updateDb=True

				if sw_updateDb:
					try:
						cmd="mysql_upgrade"
						os.system(cmd)
					except Exception as e:
						print e

				self._fix_root_pwd()
				return [True,""]

		except Exception as e:
			print e
			return [False,str(e)]
		#Tmpdir is now ready

	def _fix_root_pwd(self):
		cmd='/usr/sbin/lliurex-sgbd --upgrade lliurex-'+self.app
		os.system(cmd)
		
	#_fix_root_pwd

	def existsDb(self,dbName):
		cmd='/usr/sbin/lliurex-sgbd --db_is_present ' + dbName
		try:
			sp=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
			output=sp.communicate()
			dbExists=str(output[0])
	 		if dbExists.rstrip() == 'YES':
				dbExists=True
			else:
				dbExists=False
		except:	
			dbExists=False
		return dbExists

	def dumpDb(self,db,path='/tmp'):
		try:
			dbName=self.get_db_name(db)
			if self.existsDb(dbName):
				dbUser='root'
#				dbPass=''
#				for dbFile in list(self.apps_dbFiles[db]):
#					if "debian-db.php" in dbFile:
#						for line in open(dbFile):
#							if "dbuser" in line:
#								dbUser=str(line.split("=")[-1])
#								dbUser=dbUser.rstrip()
#								dbUser=dbUser[:-1]
#							elif "dbpass" in line:
#								dbPass=str(line.split("=")[-1])
#								dbPass=dbPass.rstrip()
#								dbPass=dbPass[:-1]
#							if (dbUser!='' and dbPass!=''):
#								break
#					if (dbUser!='' and dbPass!=''):
#						break
#				if (dbUser!='' and dbPass!=''):
				cmd='mysqldump --single-transaction --default-character-set=utf8 --routines --databases ' + dbName + ' --flush-privileges -u' + dbUser +' -p$(mysql_root_passwd -g)' + ' ' + dbName + '  > ' + path + '/' + dbName + '.sql'
				os.system(cmd)
				return path+'/'+ dbName+".sql"
			else:
				return ''
                except Exception as e:
			print e
			pass
	
	def restoreDb(self,dbDump_path):
		try:
			cmd="mysql -u root -p$(mysql_root_passwd -g) < "+ dbDump_path
			os.system(cmd)
		except Exception as e:
			print e
			return [False,str(e)]
	
