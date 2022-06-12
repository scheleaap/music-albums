'''Empties mp3 files.'''

'''
Directories that are skipped:
!
_
@
'''

import argparse
import fnmatch
import logging
import os
import re

print 'Remove the following line to enable this script, but only if you\'re sure.'
exit()

RE_MUSIC_FILES = re.compile(r'.*\.(mp3|ogg|wma|mpc|flac|m4a|mp3\.niet_luisteren)$', re.IGNORECASE)

def listdir_with_fnmatch(path, pattern):
	'''Lists all files in a directory whose file names match a shell-style pattern.
	
	This is the same as os.listdir() combined with fnmatch.filter().
	'''
	return fnmatch.filter(os.listdir(path), pattern)

def listdir_with_re(path, re_obj):
	'''Lists all files in a directory whose file names match a regular expression pattern.
	
	This is the same as os.listdir() combined with fnmatch.filter().
	'''
	return [dir_name for dir_name in os.listdir(path) if re_obj.match(dir_name)]

def empty_file(path):
	times = os.stat(path)
	with open(path, 'w'):
		pass
	os.utime(path, (times.st_atime, times.st_mtime))

def process_directory(base_path):
	for dir_name in list_directories(base_path):
		dir_path = os.path.join(base_path, dir_name)
		if dir_matches(dir_path):
			logging.info('Processing {}'.format(dir_path))
			
			# Recurse.
			process_directory(dir_path)
			
			# Process mp3's.
			for file_name in listdir_with_re(dir_path, RE_MUSIC_FILES):
				file_path = os.path.join(dir_path, file_name)
				try:
					if os.path.getsize(file_path) > 0:
						logging.debug('Processing {}'.format(file_path))
						empty_file(file_path)
				except WindowsError as e:
					logging.error(e)
		else:
			#logging.debug('Skipping {}'.format(dir_path))
			pass

def list_directories(path):
	'''Returns a list of all directories in a directory.'''
	return [dir_name for dir_name in os.listdir(path) if os.path.isdir(os.path.join(path, dir_name))]

def dir_matches(path):
	_parent, dir_name = os.path.split(path)
	
	if dir_name.startswith('!'):
		return False
	elif dir_name.startswith('@'):
		return False
	elif dir_name.startswith('_'):
		return False
	else:
		return True
	
if __name__ == '__main__':
	# Parse command-line options.
	args = argparse.ArgumentParser(
			description=__doc__,
			formatter_class=argparse.RawDescriptionHelpFormatter
			)
	args.add_argument('dir', help='The directory to process.')
	args = args.parse_args()
	
	# Initialize logging.
	logging.basicConfig(
			level=logging.WARN,
			format='%(levelname)s %(message)s',
			)
	
	process_directory(args.dir)
