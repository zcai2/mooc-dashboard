import requests,datetime,mysql.connector,os,errno
from login import login
from csvToSQL import CSV_TO_SQL

def download(s, uni_name, course_name, run, info):
	""" Fetch all the datasets (CSV) for a given iteration (run) of a course

	:param s: BeautifulSoup Session
	:param uni_name: (string) The Institution name
	:param course_name: (string) The name of the course
	:param run: (integer) The iteration of the course
	:param info: (dictionary) Metadata about the course / run
	:return:
	"""

	start_date = info['start_date'].strftime('%Y-%m-%d')
	end_date = info['end_date'].strftime('%Y-%m-%d')

	dir_path = "../data/" + uni_name + "/" + course_name + "/" + run +" - "+ start_date + " - "+end_date
	print "Considering: %s (%s, %s - %s) status: [%s] ..." % (course_name, run, start_date, end_date,  info['status'])

	if info['status'] == 'in progress' or not os.path.isdir(dir_path):
		#We only fetch data for course runs that are currently in progress, or about which we know nothing.
		print "Creating output directory: %s" % dir_path
		try:
			os.makedirs(dir_path)
		except OSError as exc:
			if exc.errno == errno.EEXIST:
				pass
			else:
				raise

		#Create course metadata file
		f_metadata_csv = open(dir_path+"/metadata.csv",'w')
		f_metadata_csv.write("uni_name,course_name,run,start_date,end_date,duration_weeks"+'\n')
		f_metadata_csv.write(uni_name+","+course_name+","+run+","+start_date+","+end_date+","+info['duration_weeks']+'\n')
		f_metadata_csv.close()

		#fetch the CSVs
		for url,filename in info['datasets'].items():
				print "Downloading %s to %s ..." % (url, dir_path)
				dow = s.get(url)
				f = open(dir_path+"/"+filename,'wb')
				f.write(dow.content)
				print "...done"
				f.close()
				s.close()
	else:
			print "output directory: %s exists and course is finished - skipping download " % dir_path


def importData(files,uni):
	
	sql = mysql.connector.connect(host = 'localhost',user= 'mooc',password = 'changeMe',database = 'moocs')
	convert = CSV_TO_SQL(sql)
	
	for f,course_run in files.items():
		convert.insertIntoTable(f,course_run,uni)
		os.remove(f)


