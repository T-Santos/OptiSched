from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from django.template import RequestContext, loader

from django.shortcuts import render_to_response, get_object_or_404, render, redirect

from .forms import *
from .models import *

import operator
import collections
from datetime import datetime,date, timedelta
import datetime as dt

# turning date from external to internal
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format

from django import forms

import pdb

#import MakeObject
import Workday
import ScheduleDateTimeUtilities
import ViewHelperFunctions

TIMESLICE = 30

def home(request):
	context = {}
	template = "home.html"
	return render(request,template,context)

def about(request):
	context = {}
	template = "About.html"
	return render(request,template,context)

def contact(request):
	context = {}
	template = "Contact.html"
	return render(request,template,context)

@login_required
def dashboard(request):
	# TODO: Maybe pass if the user is an employee or manager to show them a different dash
	#pdb.set_trace()
	from_date = dt.date.today() + dt.timedelta(days=3)
	recently_created_days = Date.objects.filter(
													date_user = request.user,
													date__lte = from_date,
													).order_by(
																'-date'
																)[:7]
	recently_created_shifts = Shift.objects.filter(
													shift_user = request.user,
													shift_date__lte = from_date,
													).order_by(
																'-shift_date'
																)[:5]

	recently_viewed_shifts = Shift.objects.filter(
													shift_user = request.user,
													shift_date__lte = from_date,
													).order_by(
																'-shift_date'
																)[:5]
	recently_viewed_employees = Person.objects.filter(
														person_user = request.user,
														)[:5]

	context = {
				'recently_created_days': recently_created_days,
				'recently_created_shifts': recently_created_shifts,
				'recently_viewed_shifts': recently_viewed_shifts,
				'recently_viewed_employees': recently_viewed_employees,
				}
	template = "Dashboard.html"
	return render(request,template,context)

@login_required
def settings(request):
	''' Doing some settings based setup'''

	template_redirect = 'OptiSched:dashboard'
	template = 'Settings.html'

	if request.method == 'POST':
		return HttpResponseRedirect(reverse(template_redirect))
	else:
		context = {}
		return render(request,template,context)

@login_required
def general_settings(request):
	''' Doing some settings based setup'''

	template_redirect = 'OptiSched:dashboard'
	template = 'GeneralSettings.html'

	existing_employee_types = EmployeeType.objects.filter(
															employee_type_user = request.user,
															)

	if existing_employee_types:
		employee_type_blank_lines = 1
	else:
		employee_type_blank_lines = 5

	employee_type_form = EmployeeTypesForm()

	EmployeeTypeFormSet = forms.modelformset_factory(
														EmployeeType,
														form = EmployeeTypesForm,
														extra = employee_type_blank_lines,
														can_delete = True,
														)

	if request.method == 'POST':

		employee_type_formset = EmployeeTypeFormSet(
													request.POST,
													request.FILES,
													prefix='employee_type',
													)

		# employee types
		if employee_type_formset.is_valid():

			# Delete
			for form in employee_type_formset.deleted_forms:
				if form.instance.pk:
					form.instance.delete()

			# Save
			for form in employee_type_formset:

				if (form.is_valid() 
					and form not in employee_type_formset.deleted_forms
					and form.has_changed()):
						obj = form.save(commit=False)
						obj.employee_type_user = request.user
						obj.save()

			return HttpResponseRedirect(reverse(template_redirect))

	else:

		employee_type_formset = EmployeeTypeFormSet(
														prefix='employee_type',
														queryset = existing_employee_types,
														)
	context = {
				'EmployeeTypeFormSet': employee_type_formset,
				}

	return render(request,template,context)

@login_required
def schedule_settings(request):
	''' Doing some settings based setup'''

	template_redirect = 'OptiSched:dashboard'
	template = 'ScheduleSettings.html'

	existing_requirement_day_times = RequirementDayTime.objects.filter(
																		requirement_day_time_user = request.user,
																		)

	existing_requirement_date_times = RequirementDateTime.objects.filter(
																			requirement_date_time_user = request.user,
																			)

	if existing_requirement_day_times:
		requirement_daytimes_blank_lines = 5
	else:
		requirement_daytimes_blank_lines = 5

	if existing_requirement_date_times:
		requirement_datetimes_blank_lines = 1
	else:
		requirement_datetimes_blank_lines = 3

	RequirementDayTimeFormSet = make_RequirementDayTimeForm(
																	request.user,
																	requirement_daytimes_blank_lines,
																	)
		
	RequirementDateTimeFormSet = make_RequirementDateTimeForm(
																	request.user,
																	requirement_datetimes_blank_lines,
																	)

	if request.method == 'POST':

		employee_requirement_daytime_formset = RequirementDayTimeFormSet(
																			request.POST,
																			request.FILES,
																			prefix='requirement_day_time',
																			)

		employee_requirement_datetime_formset = RequirementDateTimeFormSet(
																			request.POST,
																			request.FILES,
																			prefix='requirement_date_time',
																			)

		# Request Date times
		if employee_requirement_daytime_formset.is_valid():

			# Delete
			for form in employee_requirement_daytime_formset.deleted_forms:
				if form.instance.pk:
					form.instance.delete()

			# Save
			for form in employee_requirement_daytime_formset:

				if (form.is_valid() 
					and form not in employee_requirement_daytime_formset.deleted_forms
					and form.has_changed()):
						obj = form.save(commit = False)
						obj.requirement_day_time_user = request.user
						obj.save()

		# Request Date times
		if employee_requirement_datetime_formset.is_valid():

			# Delete
			for form in employee_requirement_datetime_formset.deleted_forms:
				if form.instance.pk:
					form.instance.delete()

			# Save
			for form in employee_requirement_datetime_formset:

				if (form.is_valid() 
					and form not in employee_requirement_datetime_formset.deleted_forms
					and form.has_changed()):
						obj = form.save(commit = False)
						obj.requirement_date_time_user = request.user
						obj.save()

		return HttpResponseRedirect(reverse(template_redirect))

	else:

		employee_requirement_daytime_formset = RequirementDayTimeFormSet(
																			prefix='requirement_day_time',
																			queryset = existing_requirement_day_times,
																			)

		employee_requirement_datetime_formset = RequirementDateTimeFormSet(
																			prefix='requirement_date_time',
																			queryset = existing_requirement_date_times,
																			)
		context = {
					'RequirementDayTimeFormSet': employee_requirement_daytime_formset,
					'RequirementDateTimeFormSet': employee_requirement_datetime_formset,
					}

	return render(request,template,context)

@login_required
def create_new_employee(request):
	''' Doing some settings based setup'''

	template_redirect = 'OptiSched:dashboard'
	template = 'CreateEmployee.html'

	if request.method == 'POST':

		employee_info_form = EmployeeInfoForm(request.POST)

		if employee_info_form.is_valid():

			if 'SaveAndDash' in request.POST:
				obj = employee_info_form.save(commit = False)
				obj.person_user = request.user
				obj.save()
				return HttpResponseRedirect(reverse(template_redirect))
			elif 'SaveAndAnother' in request.POST:
				obj = employee_info_form.save(commit = False)
				obj.person_user = request.user
				obj.save()
				return HttpResponseRedirect('')
			else:
				empoyee_info_form = EmployeeInfoForm()
				context = {
							'EmployeeInfoForm': employee_info_form,
						}

		else:
			print("not valid input")
			context = {
						'EmployeeInfoForm':EmployeeInfoForm,
					}

	else:
		employee_info_form = EmployeeInfoForm()
		context = {
					'EmployeeInfoForm': employee_info_form,
				}
	return render(request,template,context)

@login_required
def edit_employee(request,employee_id):
	''' Doing some settings based setup'''

	# Determine if we can access the page/employee we are trying to edit
	try:
		employee = Person.objects.get(
										pk = employee_id,
										person_user = request.user,
										)
	except Person.DoesNotExist:
		raise Http404("Employee does not exist")
	#employee = get_object_or_404(Person,employee_id)	

	# Set up vars
	template_redirect = 'OptiSched:dashboard'
	template = 'EditEmployee.html'

	employee_info_form = EmployeeInfoForm(instance = employee)

	existing_request_daytimes = RequestDayTime.objects.filter(
																request_day_time_user = request.user,
																rqst_day_employee = employee,
																).order_by(
																			'day_of_week',
																			'rqst_day_type',
																			)

	existing_request_datetimes = RequestDateTime.objects.filter(
																request_date_time_user = request.user,
																rqst_date_employee = employee,
																).order_by(
																			'rqst_date_date',
																			'rqst_date_type',
																			)

	existing_employee_types = PersonEmployeeType.objects.filter(
																person_employee_type_user = request.user,
																pet_employee = employee,
																)

	# determine number of blank lines
	if existing_request_daytimes:
		daytime_request_blank_forms = 1
	else:
		daytime_request_blank_forms = 5	

	if existing_request_datetimes:
		datetime_request_blank_forms = 1
	else:
		datetime_request_blank_forms = 5		

	EmployeeRequestDayTimeFormSet = forms.modelformset_factory(
																	RequestDayTime,
																	form = EmployeeRequestDayTimeForm,
																	extra = daytime_request_blank_forms,
																	can_delete = True,
																	)

	EmployeeRequestDateTimeFormSet = forms.modelformset_factory(
																	RequestDateTime,
																	form = EmployeeRequestDateTimeForm,
																	extra = datetime_request_blank_forms,
																	can_delete = True,
																	)

	EmployeeEmployeeTypeFormSet = make_EmployeeEmployeeTypeForm(
																	request.user,
																	1,
																	)

	if request.method == 'POST':

		employee_request_daytime_formset = EmployeeRequestDayTimeFormSet(
																			request.POST,
																			request.FILES,
																			prefix='request_day_time',
																			)

		employee_request_datetime_formset = EmployeeRequestDateTimeFormSet(
																			request.POST,
																			request.FILES,
																			prefix='request_date_time',
																			)

		employee_employeetype_formset = EmployeeEmployeeTypeFormSet(
																	request.POST,
																	request.FILES,
																	prefix='employee_type',
																	)

		# Request Date times
		if employee_request_datetime_formset.is_valid():

			# Delete
			for request_form in employee_request_datetime_formset.deleted_forms:
				if request_form.instance.id:
					request_form.instance.delete()

			# Save
			for request_form in employee_request_datetime_formset:

				if (request_form.is_valid() 
					and request_form not in employee_request_datetime_formset.deleted_forms
					and request_form.has_changed()):
						obj = request_form.save(commit = False)
						obj.rqst_date_employee = employee
						obj.request_date_time_user = request.user
						obj.save()

		# Request Day Times
		if employee_request_daytime_formset.is_valid():

			# Delete
			for request_form in employee_request_daytime_formset.deleted_forms:
				if request_form.instance.id:
					request_form.instance.delete()

			# Save
			for request_form in employee_request_daytime_formset:

				if (request_form.is_valid()
					and request_form not in employee_request_daytime_formset.deleted_forms
					and request_form.has_changed()):
						obj = request_form.save(commit = False)
						obj.rqst_day_employee = employee
						obj.request_day_time_user = request.user
						obj.save()

		# Request Day Times
		if employee_employeetype_formset.is_valid():

			# Delete
			for form in employee_employeetype_formset.deleted_forms:
				if form.instance.pk:
					form.instance.delete()

			# Save
			for form in employee_employeetype_formset:

				if (form.is_valid()
					and form not in employee_employeetype_formset.deleted_forms
					and form.has_changed()):
						obj = form.save(commit = False)
						obj.pet_employee = employee
						obj.person_employee_type_user = request.user
						obj.save()

		return HttpResponseRedirect(reverse(template_redirect))
	else:

		employee_request_datetime_formset = EmployeeRequestDateTimeFormSet(
																			prefix='request_date_time',
																			queryset = existing_request_datetimes,
																			)

		employee_request_daytime_formset = EmployeeRequestDayTimeFormSet(
																			prefix='request_day_time',
																			queryset = existing_request_daytimes,
																			)

		employee_employeetype_formset = EmployeeEmployeeTypeFormSet(
																		prefix='employee_type',
																		queryset = existing_employee_types,
																		)
		context = {
					'IdentifiedEmployee': employee,
					'EmployeeInfoForm':employee_info_form,
					'EmployeeRequestDayTimeFormSet': employee_request_daytime_formset,
					'EmployeeRequestDateTimeFormSet': employee_request_datetime_formset,
					'EmployeeEmployeeTypeFormSet': employee_employeetype_formset,
					}
	return render(request,template,context)		

@login_required
def employee_list(request):

	template = 'EmployeeList.html'
	employee_list = Person.objects.filter(
											person_user = request.user,
											)
	context = {
				'EmployeeList':employee_list,
				}
	return render(request,template,context)

@login_required
def create_schedule(request):
	template_stay = 'CreateSchedule.html'
	template_redirect = 'OptiSched:ViewManagerDay'

	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = CreateDateForm(request.POST)
		context = {'CreateDateForm': form}
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			new_date = date_external = form.cleaned_data['f_date']
			start_time = form.cleaned_data.get('f_start_time')
			end_time = form.cleaned_data.get('f_end_time')

			request.session['DATE_STR'] = new_date.isoformat()

			a_workday = Workday.CreateDay(
											user = request.user,
											date = new_date,
											date_start_time = start_time,
											date_end_time = end_time,
											timeslice = TIMESLICE,
										)
			a_workday.GenerateShifts()
			a_workday.Save()
			return HttpResponseRedirect(reverse(template_redirect))
	else:
		form = CreateDateForm()
		context = {'CreateDateForm': form}
	
	return render(request,template_stay,context)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

@login_required
def create_date_span(request):

	template = "CreateDateSpan.html"
	template_redirect = "OptiSched:ViewManagerDay"

	if request.method == 'POST':

		form = CreateDateSpanForm(data = request.POST)

		if form.is_valid():

			from_date = form.cleaned_data.get('f_from_date')
			thru_date = form.cleaned_data.get('f_thru_date')
			#from_date_obj = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
			#thru_date_obj = dt.datetime.strptime(thru_date, "%Y-%m-%d").date()

			start_time = form.cleaned_data.get('f_start_time')
			end_time = form.cleaned_data.get('f_end_time')

			#start_time_obj = dt.datetime.strptime(start_time, "%H:%M:%S").time()
			#end_time_obj = dt.datetime.strptime(end_time, "%H:%M:%S").time()


			all_dates = []

			# create and populate dates
			for single_date in daterange(from_date,thru_date):

				a_workday = Workday.CreateDay(
												user = request.user,
												date = single_date,
												date_start_time = start_time,
												date_end_time = end_time,
												timeslice = TIMESLICE)
				a_workday.GenerateShifts()

				all_dates.append(a_workday)
			
			# save all dates
			for workday in all_dates:
				workday.Save()

			request.session['DATE_STR'] = from_date.isoformat()
			return HttpResponseRedirect(reverse(template_redirect))
	else:        

		form = CreateDateSpanForm(data = request.GET)

	context = {
				'DateSpanForm': form,
			}
	return render(request,template,context)

@login_required
def ViewManagerDay(request):

	template = 'ViewManagerDay.html'

	if request.method == 'POST':
		"View does not accept POSTs"
	else:

		form = NavDateForm(data = request.GET)

		if request.GET.get('navdate',False):
			date = request.GET['navdate']
		else:
			date = dt.datetime.today().strftime("%Y-%m-%d")			

		if date:
			try:
				work_day = Date.objects.get(
											date_user = request.user,
											date=date,
											)
				shifts_per_date = Shift.objects.filter(
														shift_user = request.user,
														shift_date=work_day,
														)
				shifts_per_date = sorted(shifts_per_date, key=operator.attrgetter('start_time'))

				date_error_groups = ViewHelperFunctions.ConvertErrorsToGroups(
																				work_day,
																				request.user,
																				)
				date_error_groups_compressed = ViewHelperFunctions.CompressErrorGroupsToStrings(
																									work_day.date,
																									date_error_groups,
																									TIMESLICE,
																									)
				date_error_strings = ViewHelperFunctions.ConvertCompressedErrorsToStrings(
																							date_error_groups_compressed
																							)
				
				context = {
							'NavDateForm': form,
							'work_day_display': work_day.date_display,
	   						'shifts': shifts_per_date,
			   				'date_errors':date_error_strings,
	   					}
			except ObjectDoesNotExist:
				context = {
						'NavDateForm': form,							
						'Error': "No Schedule For Date",
						}
		else:
			context = {
					'NavDateForm': form,
				}

	return render(request,template,context)

@login_required
def ViewEmployeeWeek(request,employee_id,date):


	template = 'ViewEmployeeWeek.html'

	if request.method == 'POST':
	
		navform = NavDateForm(request.POST)

		if navform.is_valid():
        	# process the data in form.cleaned_data as required
			#date_external = navform.cleaned_data['navdate']
			#dateformat = DateFormat(date_external)
			#date = dateformat.format('Y-m-d')

			date = navform.cleaned_data['navdate']
			
			if date:
				return redirect('OptiSched:ViewEmployeeWeek',employee_id,date.isoformat())
	else:
		#pdb.set_trace()
		work_day = Date.objects.get(
									date_user = request.user,
									date=date,
									)
		employee = Person.objects.get(
										pk=employee_id,
										person_user = request.user,
										)
		start_end_week_dates = ScheduleDateTimeUtilities.get_dates_from_week(
																				work_day.date.isocalendar()[0],
																				work_day.date.isocalendar()[1]
																			)
		shifts_in_week = Shift.objects.filter(
												shift_user = request.user,
												shift_date__gte = start_end_week_dates[0],
												shift_date__lte = start_end_week_dates[1],
												employee = employee
											)
		
		navform = NavDateForm(initial={'navdate': date})

		context = {
					'employee': employee,
					'shifts': shifts_in_week,
					'NavDateForm': navform,
					'week_start_date':start_end_week_dates[0],
					'week_end_date':start_end_week_dates[1],
				}
		return render(request,template,context)





