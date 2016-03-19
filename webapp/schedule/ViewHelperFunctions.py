import pdb

import datetime as dt


from .models import EmployeeTypeShiftError
import ScheduleDateTimeUtilities

def ConvertErrorsToGroups(date):
	'''
		Get errors for date and group them by employee type
	'''
	errors = EmployeeTypeShiftError.objects.filter(
													error_date = date
													).order_by(
																'error_emp_type',
																'error_time'
															)

	'''
		map of 
		{ employee type: [errors associated early to late]}
	'''
	error_groups = {}
	for error in errors:
		if error.error_emp_type.et_type in error_groups:
			error_groups[error.error_emp_type.et_type].append(error)
		else:
			error_groups[error.error_emp_type.et_type] = [error]

	return error_groups

def CompressErrorGroupsToStrings(date,error_groups,time_slice_amt):
	'''
		Create map of 
		{employee type: [[starttime,endtime],[starttime,endtime]]}
	'''
	compressed_error_groups = {}

	for employee_type,error_list in error_groups.iteritems():
		
		start_time = None
		end_time = None

		for error in error_list:
			
			# if we have an end time
			# and the next end time isnt the same as the current, store the 
			# grouping (start - end)
			if ( end_time
				and not (error.error_time == end_time)
				):
				if employee_type in compressed_error_groups:
					compressed_error_groups[employee_type].append([start_time,end_time])
				else:
					compressed_error_groups[employee_type] = [[start_time,end_time]]

				start_time = None
				end_time = None
			# the next end time is the same as the current end time
			# so update it	
			else:
				end_time = error.error_time

			if not start_time:
				start_time = error.error_time

			end_datetime = dt.datetime.combine(date,error.error_time)

			end_datetime = end_datetime + dt.timedelta(minutes=time_slice_amt)

			end_time = end_datetime.time()

		# if from the very beginning 
		# we dont have an employee to fill a shift  		
		if employee_type in compressed_error_groups:
			compressed_error_groups[employee_type].append([start_time,end_time])
		else:
			compressed_error_groups[employee_type] = [[start_time,end_time]]

	return compressed_error_groups

def ConvertCompressedErrorsToStrings(compressed_error_groups):
	
	error_strings = []

	for employee_type,range_list in compressed_error_groups.iteritems():

		for time_list in range_list:

			try:
				start_time = time_list[0]
			except IndexError:
				start_time = 'UNKNOWN'

			try:
				end_time = time_list[1]
			except IndexError:
				end_time = 'UNKNOWN'

			text = ("We could not find an available " +
					employee_type +
					" to fill the timeslot from " +
					start_time.strftime('%I:%M %p') +
					" to " +
					end_time.strftime('%I:%M %p'))
			error_strings.append(text)

	return error_strings



			