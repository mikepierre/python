import subprocess
import os
import time
import datetime
from PIL import Image
import threading
import Queue
import re
#import psycopg2

lsdir = "/webapps/hello_django/static/dummy/vd/"
rootdir = '/webapps/hello_django/static/dummy/th/'
logfile =  "/webapps/hello_django/static/dummy/read.txt"
sqlfile =  "/webapps/hello_django/static/dummy/sql.txt"
lsdirs = os.listdir(lsdir)

f = open(logfile, 'a')
s = open(sqlfile, 'a')
THdir = []

# curtime =  int(time.time())
# for vs in lsdirs:	
# 	#videofile = lsdir + vs
# 	filename = lsdir + vs
# 	extension = os.path.splitext(filename)[1]
# 	curtime += 1
# 	new_file_name = lsdir + 'VD_%s%s' % (curtime, extension)
# 	os.rename(filename, new_file_name)

exitFlag = 0

class myThread (threading.Thread):
	def __init__(self, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
	def run(self):
		#print "Starting " + self.name
		process_data(self.threadID,self.name, self.q)
		#print "Exiting " + self.name

def seconds_minutes(seconds):
	minutes = seconds / 60
	seconds = seconds % 60
	return "%02d:%02d" % (minutes,seconds)

def process_data(id,threadName, q):
	global lsdir,rootdir
	while not exitFlag:
		queueLock.acquire()
		if not workQueue.empty():
			vs = q.get()
			videofile = lsdir + vs
			curnum =  re.search(r'\d+', vs).group(0)

			vruntime = subprocess.check_output("avconv -i %s 2>&1 | grep Duration | awk '{print $2}' | tr -d ," %(videofile), shell=True)
			
			x = time.strptime(vruntime .rstrip('\r\n'),'%H:%M:%S.%f')
			videoruntime = int(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())
			f.write("\n %s" % videoruntime)
			if videoruntime > 60 :
				voffset = int (videoruntime / 10)
				vtime = videoruntime  - (voffset/2)
				index=1				

				for num in range(0,vtime,voffset):
					
					if num == 0:
						num = voffset / 2	
					throotdir =  rootdir + "TH_%s" % curnum
					thdir =  throotdir + "/%s" % curnum
					Tdir =  "TH_%s/%s"  % (curnum,curnum)
					if Tdir not in THdir:
						THdir.append(Tdir)
					imagefile =  thdir + "/%s.jpg" % (index)
					mimagefile = throotdir + "/v_%s.jpg" % (curnum)
					if not os.path.exists(throotdir):
						os.makedirs(throotdir)
						os.makedirs(thdir)
					if index == 5:
						process = subprocess.check_output("avconv -ss %s -i %s -qscale:v 2 -vframes 1 -s 638x504  %s" %(num,videofile,mimagefile),shell=True)	
					process = subprocess.check_output("avconv -ss %s -i %s -qscale:v 2 -vframes 1 -s 160x120  %s" %(num,videofile,imagefile),shell=True)	
					# print "avconv  -itsoffset -%s  -i %s -vcodec mjpeg -vframes 1 -an -f rawvideo -s 638x504 %s"  % (num,videofile, imagefile)
					
					if index == 10:
						vindex=1
						new_im = Image.new('RGB', (1600,120))
						spimagefile = throotdir + "/sp_%s.jpg" % (curnum)
						SpriteImageUrl = "TH_%s/sp_%s.jpg" % (curnum,curnum)
						ThumbnailUrl = "TH_%s/v_%s.jpg" % (curnum,curnum)
						for i in xrange(0,1600,160):
							imagefile = thdir + "/%s.jpg" % (vindex)
							im = Image.open(imagefile)
							new_im.paste(im, (i,0))
							#print imagefile
							vindex +=1
						new_im.show()
						new_im.save(spimagefile)
						sqlline = 'INSERT INTO bucketboob_video ( "user_id", "Title", "Description", "ThumbnailUrl","SpriteImageUrl", "VideoUrl", "Slug", "RunTime", "Views", "Likes", "Dislikes","Vote","IsPromoted","IsActive","IsDeleted","created", "updated") VALUES' +" ('1','NULL','', '%s',  '%s', '%s','',   '%s' ,'','','','','0','1','0','2015-09-23 17:19:01-04', '2015-09-23 17:20:35.141236-04')" % (ThumbnailUrl,SpriteImageUrl,vs,seconds_minutes(videoruntime))
						s.write('\n' + sqlline)
					# else:
					f.write("\n index:%s - num:%s - voffset:%s - vtime-%s" % (index,num,voffset,vtime))
					index +=1
			 	f.write("\n \n")
				

			queueLock.release()
			#print "curnum:%s  - %s processing %s \n\n" % (curnum,threadName, vs)
		else:
			queueLock.release()
		time.sleep(1)


#threadList = ["Thread-1", "Thread-2", "Thread-3"]
queueLock = threading.Lock()
workQueue = Queue.Queue()
threads = []
#threadID = 1

# Create new threads
#for tName in threadList:
for threadID in range(1):
	tName = "Thread-%s" % threadID
	thread = myThread(threadID, tName, workQueue)
	thread.start()
	threads.append(thread)

# Fill the queue
queueLock.acquire()
for vs in lsdirs:
	workQueue.put(vs)
queueLock.release()

# Wait for queue to empty
while not workQueue.empty():
	pass

# Notify threads it's time to exit
exitFlag = 1

# Wait for all threads to complete
for t in threads:
	t.join()
print "Exiting Main Thread"


f.close()
s.close()

# for vs in lsdirs: 
# 	curtime =  int(time.time())
# 	#videofile = lsdir + vs
# 	filename = lsdir + vs
# 	extension = os.path.splitext(filename)[1]
# 	new_file_name = lsdir + 'VD_%s%s' % (curtime, extension)
# 	os.rename(filename, new_file_name)

	# videofile = new_file_name
	#print videofile
	# vruntime = subprocess.check_output("avconv -i %s 2>&1 | grep Duration | awk '{print $2}' | tr -d ," %(videofile), shell=True)
	# #print vruntime
	# x = time.strptime(vruntime .rstrip('\r\n'),'%H:%M:%S.%f')
	# videoruntime = int(datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds())

	# if videoruntime > 60 :
	# 	voffset = int (videoruntime / 10)
	# 	vtime = videoruntime  - voffset
	# 	index=1
		

	# 	for num in range(0,vtime,voffset):
	# 		if num == 0:
	# 			num = voffset / 2	
	# 		throotdir =  rootdir + "TH_%s" % curtime
	# 		thdir =  throotdir + "/%s" % curtime
	# 		Tdir =  "TH_%s/%s"  % (curtime,curtime)
	# 		if Tdir not in THdir:
	# 			THdir.append(Tdir)
	# 		imagefile =  thdir + "/%s.jpg" % (index)
	# 		mimagefile = throotdir + "/v_%s.jpg" % (curtime)
	# 		if not os.path.exists(throotdir):
	# 			os.makedirs(throotdir)
	# 			os.makedirs(thdir)
	# 		if index == 5:
	# 			process = subprocess.check_output("avconv -ss %s -i %s -qscale:v 2 -vframes 1 -s 638x504  %s" %(num,videofile,mimagefile),shell=True)	
	# 		process = subprocess.check_output("avconv -ss %s -i %s -qscale:v 2 -vframes 1 -s 150x120  %s" %(num,videofile,imagefile),shell=True)	
	# 		#print "avconv  -itsoffset -%s  -i %s -vcodec mjpeg -vframes 1 -an -f rawvideo -s 638x504 %s"  % (num,videofile, imagefile)
	# 		index +=1
	# 		#print num
	# 		#num +=thstart
	# 	if index !=1:
	# 		f.write("\n Thumb 10 = ok - ThumbnailUrl = ok - ")
	

# def seconds_minutes(seconds):
# 	minutes = seconds / 60
# 	seconds = seconds % 60
# 	return "%02d:%02d" % (minutes,seconds)
# print THdir
'''# save stripe image to one image
for vs in lsdirs: 
curtime =  int(time.time())	
vindex=1;
new_im = Image.new('RGB', (1500,120))
spimagefile = throotdir + "/sp_%s.jpg" % (curtime)
# SpriteImageUrl = "TH_%s/sp_%s.jpg" % (curtime,curtime)
# ThumbnailUrl = "TH_%s/v_%s.jpg" % (curtime,curtime)
for i in xrange(0,1500,150):
	imagefile = thdir + "/%s.jpg" % (vindex)
	im = Image.open(imagefile)
	new_im.paste(im, (i,0))
	#print imagefile
	vindex +=1
new_im.show()
new_im.save(spimagefile)
# sqlline = 'INSERT INTO bucketboob_video ( "user_id", "Title", "Description", "ThumbnailUrl","SpriteImageUrl", "VideoUrl", "Slug", "RunTime", "Views", "Likes", "Dislikes","Vote","IsPromoted","IsActive","IsDeleted","created", "updated") VALUES' +" ('1','NULL','', '%s',  '%s', '%s','',   '%s' ,'','','','','0','1','0','2015-09-23 17:19:01-04', '2015-09-23 17:20:35.141236-04')" % (ThumbnailUrl,SpriteImageUrl,vs,seconds_minutes(videoruntime))
# f.write("SpriteImageUrl = ok")
# s.write('\n' + sqlline)
# time.sleep(10)'''
