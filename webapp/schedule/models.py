import datetime
import time
#import datetime as dt

from django.db import models
from django.utils import timezone 

from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db.models import permalink

from django.contrib.auth.models import User

# Create Shift Error logging
# Date and Error Code (internal / external)

class Person(models.Model):

	person_user = models.ForeignKey(
									User,
									verbose_name="User",
									)
	
	first_name = models.CharField(
									max_length=60,
									verbose_name="First Name",
									)
	last_name = models.CharField(
									max_length=60,
									verbose_name="Last Name",
									)

	# min max hours to work per week
	person_min_hours_per_week = models.PositiveIntegerField(
															default=25,
															verbose_name='Min Hrs / Week',
															)

	person_max_hours_per_week = models.PositiveIntegerField(
															default=40,
															verbose_name='Max Hrs / Week',
															)

	# min max hours to work per shift
	person_min_hours_per_shift = models.PositiveIntegerField(
																default=4,
																verbose_name='Min Hrs / Shift',
																)
	person_max_hours_per_shift = models.PositiveIntegerField(
																default=8,
																verbose_name='Max Hrs / Shift',
																)
	def clean(self):

		if not (self.person_min_hours_per_shift <= self.person_max_hours_per_shift):
			raise ValidationError("Min Hours larger than Max Hours (per shift)")

		if not (self.person_min_hours_per_week <= self.person_max_hours_per_week):
			raise ValidationError("Min Hours larger than Max Hours (per week)")

	def name(self):
        	return ''.join([self.last_name,',', self.first_name])

	def name_normal(self):
        	return ''.join([self.first_name,' ',self.last_name])

	def name_normal_id(self):
        	return ''.join([self.first_name,' ',self.last_name,'(id:',str(self.id),')'])

	def get_edit_url(self):
		#"http://localhost:8000/OptiSched/EditEmployee/1
		path = '/OptiSched/EditEmployee/' + str(self.pk)
		return path

	def __str__(self):             	
	        #return str(self.name()) + ' (id: ' + str(self.id) + ')'
		return str(self.name())

class PersonEmployeeType(models.Model):

	person_employee_type_user = models.ForeignKey(
													User,
													verbose_name="User",
													)
	
	# employee
	pet_employee = models.ForeignKey(
										Person,
										verbose_name="Employee",
										)

	# employee type
	pet_employee_type = models.ForeignKey(
											'EmployeeType',
											verbose_name="Position",
											)

	# Members
	
	def __str__(self):
		return str(self.pet_employee) + ' ' + str(self.pet_employee_type)


class Shift(models.Model):

	shift_user = models.ForeignKey(
									User,
									verbose_name="User",
									)

	# date for shift
	shift_date = models.ForeignKey(
									'Date',
									verbose_name="Shift Date",
									)
	
	# employee on shift	
	employee = models.ForeignKey(
									Person,
									verbose_name="Employee",
									)

	# Employee Type for employee
	# TODO: Limit choices to the employee's employee types?
	shift_employee_type = models.ForeignKey(
												'EmployeeType',
												verbose_name="Position",
												)
	start_time = models.TimeField("Start Time")
	end_time = models.TimeField("End Time")

	def before_working_day_pc(self):
		return ((self.start_time.hour / float(24) ) * 100)

	def working_day_pc(self):
		return (((self.end_hour() - self.start_time.hour) /  float(24) ) * 100)

	def hours(self):
		start_hours = self.start_time.hour
		end_hours = self.end_hour()
		duration = end_hours - start_hours
		return abs(duration)

	def end_hour(self):
		
		if (self.end_time.hour == 23 and
		    self.end_time.minute > 0 ):
			end_hours = 24
		elif (self.end_time.hour == 0 and
		      self.end_time.minute == 0):
			end_hours = 24
		elif (self.end_time.hour == 0 and
		      self.end_time.minute > 0):
			end_hours = 1
		else:
			end_hours = self.end_time.hour
		return end_hours
		
	def hour_list(self):
		return list(range(self.start_time.hour,self.end_hour()))

	def hours_disp(self):
		return str(self.hours())		

	def get_week(self):
		return self.shift_date.date.isocalendar()[1]
	#get_week.short_description = "week"

	def get_employee_week_url(self):
		return reverse('OptiSched:ViewEmployeeWeek',kwargs={'employee_id': self.employee.id,
															'date': self.shift_date.date.isoformat(),})

	def display_details(self):
		return str(self.employee.name()) + ' Position: ' + str(self.shift_employee_type) + ' For: ' + self.hours_disp() + ' hours'

	def display_shift_details(self):
		return (str(self.shift_date.day_of_week()) + ' ' + str(self.shift_date.date))

	def __str__(self):
		return self.display_details()

class Date(models.Model):

	date_user = models.ForeignKey(
									User,
									verbose_name="User",
									)

	date = models.DateField(
							primary_key=True,
			        		default=datetime.date.today,
			        		verbose_name="Date",
			        		)
	# Schedule Params
	day_start_time = models.TimeField(
										"Day Start Time",
				          				default = datetime.time(8,0,0),
				          				)

	day_end_time = models.TimeField(
									"Day End Time",
				       				 default = datetime.time(23,0,0),
				       				 )

	def get_absolute_url(self):
		#"http://localhost:8000/OptiSched/ViewManagerDay/?navdate=2016-02-14"
		path = '/OptiSched/ViewManagerDay/' + '?navdate=' + self.date.isoformat()
		return path
	
	def total_hours(self):
		start_hours = self.day_start_time.hour
		if (self.day_end_time.hour == 23 and
		    self.day_end_time.minute > 0 ):
			end_hours = 24
		elif (self.day_end_time.hour == 0 and
		      self.day_end_time.minute == 0):
			end_hours = 24
		elif (self.day_end_time.hour == 0 and
		      self.day_end_minute > 0):
			end_hours = 1
		else:
			end_hours = self.day_end_time.hour
		duration = end_hours - start_hours
		return abs(duration)

	# is holiday YN BooleanField property
	def day_of_week(self):
		dow = self.date.weekday()
    		if dow == 0:
        		dow = 'Monday'
    		elif dow == 1:
        		dow = 'Tuesday'
    		elif dow == 2:
        		dow = 'Wednesday'
    		elif dow == 3:
        		dow = 'Thursday'
    		elif dow == 4:
        		dow = 'Friday'
    		elif dow == 5:
        		dow = 'Saturday'
    		elif dow == 6:
        		dow = 'Sunday'
    		else:
        		dow = 'Undefined'
		return dow		

	def week(self):
		return self.date.isocalendar()[1]

	def date_display(self):
        	 return self.day_of_week() + ' ' + str(self.date) + ' ' + 'week: ' + str(self.week())

	def __str__(self):
		return str(self.date)

class EmployeeTypeShiftError(models.Model):

	employee_type_shift_error_user = models.ForeignKey(
														User,
														verbose_name="User",
														)

	# date for notification
	error_date = models.ForeignKey(
									'Date',
									verbose_name="Date",
									)

	error_time = models.TimeField("Error Time")

	# TODO Error End time...we're storing too many errors

	# Employee Type if found an error having to do with employee types
	error_emp_type = models.ForeignKey('EmployeeType')

	def error_display_time(self):
		return self.error_time.strftime('%I:%M %p')

	def error_display(self):
		text = ("We could not find an available " +
				self.error_emp_type.et_type + 
				" to fill the " + 
				self.error_time.strftime('%I:%M %p') +
				#" to " + 
				#self.ConvertTimeSliceToDateTime(timeslice+1).strftime('%I:%M %p') + 
				" timeslot based on your criteria.")

		return text

	def __str__(self):
		return str(self.error_date) + " " + self.error_display_time()

class RequestDayTime(models.Model):
	
	# store request types
	PREFERRED = 'PREF'
	SKIP = 'SKIP'

	DAYS_OF_WEEK = (
					(0,'Monday'),
					(1,'Tuesday'),
					(2,'Wednesday'),
					(3,'Thursday'),
					(4,'Friday'),
					(5,'Saturday'),
					(6,'Sunday'),
					)
	
	REQUEST_TYPES = (
	        		(PREFERRED, 'Preferred'),
	        		(SKIP, 'Cannot Work'),
	    			)

	request_day_time_user = models.ForeignKey(
												User,
												verbose_name="User",
												)

	# employee key
	rqst_day_employee = models.ForeignKey(
											Person,
											verbose_name="Employee",
											)

	# Day of the week
	day_of_week = models.IntegerField(
										choices = DAYS_OF_WEEK,
										verbose_name="Day",
										)

	# Request
	rqst_day_type = models.CharField(
    									max_length=4,
    									choices=REQUEST_TYPES,
    									verbose_name="Request Type",
    									)

	# Time the req should start
	rqst_day_start_time = models.TimeField(
											"Request Start Time",
				          					default = datetime.time(0,0,0),
				          					)
	# Time the req should stop
	rqst_day_end_time = models.TimeField(
											"Request End Time",
				          					default = datetime.time(23,59,0),
				          					)

	class Meta:
		# index_together? https://docs.djangoproject.com/en/1.9/ref/models/options/#index-together
		unique_together = (("day_of_week","rqst_day_start_time","rqst_day_type"),)

	# Members
	def __str__(self):
		return str(self.rqst_day_employee) + ' ' + str(self.get_day_of_week_display()) + ' ' + str(self.rqst_day_start_time.strftime("%H:%M")) + " " +  str(self.rqst_day_type)


class RequestDateTime(models.Model):
	# There are going to be serveral of these if a vaca spans multiple days 

	request_date_time_user = models.ForeignKey(
												User,
												verbose_name="User",
												)
	
	# store request types
	VACATION = 'VACA'
	SICK = 'SICK'
	PREFERRED = 'PREF'
	SKIP = 'SKIP'

	# date key
	# TODO: maybe need to make this required somehow
	rqst_date_date = models.DateField(
										verbose_name="Request Date",
										)

	# employee key
	rqst_date_employee = models.ForeignKey(
											Person,
											verbose_name="Request Employee",
											)

	# start and end times
	rqst_date_start_time = models.TimeField(
											"Request Start Time",
				              				default = datetime.time(0,0,0),
				              				)
	rqst_date_end_time = models.TimeField(
											"Request End Time",
				            				default = datetime.time(23,59,0),
				            				)
	
	REQUEST_TYPES = (
        		  		(VACATION, 'Vacation'),
        				(SICK, 'Sick'),
        				(PREFERRED, 'Preferred'),
        				(SKIP, 'Cannot Work'),
    				)
	
	rqst_date_type = models.CharField(
    									max_length=4,
    									choices=REQUEST_TYPES,
    									verbose_name="Request Type",
    									)

	# Members
	def displayRequestDateSpan(self):
		return str(self.rqst_date_date) + ' ' + str(self.rqst_date_start_time) + ' - ' + str(self.rqst_date_end_time)

	def __str__(self):
		return str(self.rqst_date_employee) + ' ' + self.displayRequestDateSpan() + ' ' + self.get_rqst_date_type_display()

class EmployeeType(models.Model):

	employee_type_user = models.ForeignKey(
											User,
											verbose_name="User",
											)
	
	# employee type
	et_type = models.CharField(
								max_length=60,
								verbose_name="Position",
								)

	class Meta:
		unique_together = (
							(
								"employee_type_user",
								"et_type",
								),
							)

	# Members
	def __str__(self):
		return str(self.et_type)

class RequirementDateTime(models.Model):

	requirement_date_time_user = models.ForeignKey(
													User,
													verbose_name="User",
													)

	rqmt_date_employee_type = models.ForeignKey(
													EmployeeType,
													verbose_name="Position",
													)

	# Date
	rqmt_date_date = models.DateField(
										"Effective Date",
										)
	
	# Time
	rqmt_date_time = models.TimeField(
										"Effective Time",
										)

	# Requirement
	rqmt_date_employee_count = models.PositiveIntegerField(
															"Count",
															)

	class Meta:
		unique_together = (
							(
								"rqmt_date_date",
								"rqmt_date_time",
								"rqmt_date_employee_type",
								"rqmt_date_employee_count",
								),
							)

	# Members
	def __str__(self):
		return str(self.rqmt_date_date.strftime("%Y-%m-%d")) + " " + str(self.rqmt_date_time.strftime("%H:%M")) + " " +  str(self.rqmt_date_employee_type) + " " +  str(self.rqmt_date_employee_count)

class RequirementDayTime(models.Model):

	requirement_day_time_user = models.ForeignKey(
													User,
													verbose_name="User",
													)

	days_of_week = (
					(0,'Monday'),
					(1,'Tuesday'),
					(2,'Wednesday'),
					(3,'Thursday'),
					(4,'Friday'),
					(5,'Saturday'),
					(6,'Sunday'),
					)

	# Day of the week
	day_of_week = models.IntegerField(
										choices = days_of_week,
										verbose_name="Day",
										)

	# Time the req should take effect
	rqmt_day_start_time = models.TimeField(
											"Effective Time",
				          					#default = datetime.time(0,0,0),
				          					)

	# Requirement
	rqmt_day_employee_type = models.ForeignKey(
												EmployeeType,
												verbose_name="Employee",
												)

	# Count
	rqmt_day_employee_count = models.PositiveIntegerField(
															verbose_name="Count",
															)

	class Meta:
		unique_together = (
							(
								"day_of_week",
								"rqmt_day_start_time",
								"rqmt_day_employee_type",
								"rqmt_day_employee_count",
								),
							)

	# Members
	def __str__(self):
		return str(self.get_day_of_week_display())+ ' ' + str(self.rqmt_day_start_time.strftime("%H:%M")) + " " + str(self.rqmt_day_employee_type) + " " +  str(self.rqmt_day_employee_count)



	



