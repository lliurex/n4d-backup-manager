import pwd
import grp
import os
import imp
backupmanager=imp.load_source("BackupManager","/usr/share/n4d/python-plugins/support/BackupManager.py")

class MoodleManager:
	
	def __init__(self):
		self.moodle=backupmanager.BackupManager(app='moodle')
		moodleFiles={} 
		moodleDbFiles={'moodle':['/etc/moodle/debian-db.php']} 
		moodleDirs={'moodle':['/var/lib/moodle']}

		self.moodle.set_app_files(moodleFiles)
		self.moodle.set_app_dbFiles(moodleDbFiles)
		self.moodle.set_app_dirs(moodleDirs)

	def restore(self,file_path=None):
		self.moodle.set_backup_name("MoodleManager")
		retVal=self.moodle.restore(file_path)
		self._last_actions('remove')
		return retVal

	def backup(self,dir="/backup"):
		self.moodle.set_backup_name(get_backup_name("MoodleManager"))
		retVal=self.moodle.backup(dir)
		return retVal

	def _last_actions(self,action):
		if action=='restore':
			folders_to_del=['/var/lib/moodle/cache','/var/lib/moodle/localcache','/var/lib/moodle/sessions']
			for folder in folders_to_del:
				if os.path.exists(folder):
					shutil.rmtree(folder, ignore_errors=True)
			uid = pwd.getpwnam("www.data'").pw_uid
			gid = grp.getgrnam("www-data").gr_gid
			folders_to_chown=moodleDirs['moodle']
			for folder in folders_to_chown:
				os.chown(folder, uid, gid)

