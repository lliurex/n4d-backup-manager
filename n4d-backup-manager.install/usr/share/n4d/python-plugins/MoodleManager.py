import pwd
import grp
import os
from importlib.machinery import SourceFileLoader
backupmanager=SourceFileLoader("BackupManager","/usr/share/n4d/python-plugins/support/BackupManager.py").load_module()
import n4d.responses

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
		if retVal[0]:
			return n4d.responses.build_successful_call_response(retVal[1])
		else:
			return n4d.responses.build_failed_call_response(retVal[1])

	def backup(self,dir="/backup"):
		self.moodle.set_backup_name("moodle")
		retVal=self.moodle.backup(dir)
		if retVal[0]:
			return n4d.responses.build_successful_call_response(retVal[1])
		else:
			return n4d.responses.build_failed_call_response(retVal[1])

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

