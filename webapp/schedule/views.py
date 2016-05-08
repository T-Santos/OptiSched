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

	getting_started_complete = []
	getting_started_not_complete = []

	from_date = dt.date.today() + dt.timedelta(days=3)

	recently_created_days = Date.objects.filter(
													date_user = request.user,
													date__lte = from_date,
													).order_by(
																'-date'
																)[:7]
	any_employees = Person.objects.filter(
											person_user = request.user,
											)

	any_employee_types = EmployeeType.objects.filter(
														employee_type_user = request.user,
														)
	any_person_employee_types = PersonEmployeeType.objects.filter(
																	person_employee_type_user = request.user,
																	)

	any_schedule_criteria = RequirementDayTime.objects.filter(
																requirement_day_time_user = request.user,
																)
	if not any_schedule_criteria:
		any_schedule_criteria = RequirementDateTime.objects.filter(
																	requirement_date_time_user = request.user,
																	)
	if (any_employees
		and any_employee_types
		and any_person_employee_types
		and any_schedule_criteria):
		show_getting_started = False
	else:
		show_getting_started = True

		# Should be in the order they should display on the screen		
		if any_employee_types:
			getting_started_complete.append('Add Employee Types')
		else:
			getting_started_not_complete.append('Add Employee Types')
		
		if any_employees:
			getting_started_complete.append('Add Employees')
		else:
			getting_started_not_complete.append('Add Employees')
		
		if any_schedule_criteria:
			getting_started_complete.append('Create Schedule Criteria')
		else:
			getting_started_not_complete.append('Create Schedule Criteria')
		
		if any_person_employee_types:
			getting_started_complete.append('Attach Employee Types to Employees')
		else:
			getting_started_not_complete.append('Attach Employee Types to Employees')

	context = {
				'recently_created_days': recently_created_days,
				'show_getting_started': show_getting_started,
				'getting_started_complete': getting_started_complete,
				'getting_started_not_complete': getting_started_not_complete,
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
															).order_by(
																		'et_type',
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

		validation_error_found = False

		objects_to_save = []
		objects_to_delete = []

		employee_type_formset = EmployeeTypeFormSet(
													request.POST,
													request.FILES,
													prefix = 'employee_type',
													)

		# employee types
		if employee_type_formset.is_valid():

			# Delete
			for form in employee_type_formset.deleted_forms:
				if form.instance.pk:
					objects_to_delete.append(form.instance)
			
			# Save
			# ideally would want this in formset validation
			# so that everywhere doesnt need this logic
			employee_types = []
			for form in employee_type_formset:

				if form.is_valid():

					if form not in employee_type_formset.deleted_forms:

						if form.instance.et_type:

							if form.has_changed():
								obj = form.save(commit=False)
								obj.employee_type_user = request.user
								objects_to_save.append(obj)

							if form.instance.et_type in employee_types:
								form.add_error('et_type',"Duplicate Entry")
								validation_error_found = True
							employee_types.append(form.instance.et_type)
				else:
					validation_error_found = True
		else:
			validation_error_found = True


		# if no errors, file the edits
		if not validation_error_found:

			for obj in objects_to_delete:
				obj.delete()

			for obj in objects_to_save:
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
																		).order_by(
																					'day_of_week',
																					'rqmt_day_employee_type',
																					'rqmt_day_start_time',
																					)

	existing_requirement_date_times = RequirementDateTime.objects.filter(
																			requirement_date_time_user = request.user,
																			).order_by(
																						'rqmt_date_date',
																						'rqmt_date_employee_type',
																						'rqmt_date_time',
																						)
	try:
		general_settings_instance = GeneralSetting.objects.get(
																general_setting_user = request.user,
																)

		general_settings_form = GeneralScheduleSettingsForm(
															instance = general_settings_instance,
															)
	except GeneralSetting.DoesNotExist:
		general_settings_instance = False
		general_settings_form = GeneralScheduleSettingsForm()

	if existing_requirement_day_times:
		requirement_daytimes_blank_lines = 1
	else:
		requirement_daytimes_blank_lines = 5

	if existing_requirement_date_times:
		requirement_datetimes_blank_lines = 1
	else:
		requirement_datetimes_blank_lines = 5

	RequirementDayTimeFormSet = make_RequirementDayTimeForm(
																	request.user,
																	requirement_daytimes_blank_lines,
																	)
		
	RequirementDateTimeFormSet = make_RequirementDateTimeForm(
																	request.user,
																	requirement_datetimes_blank_lines,
																	)

	if request.method == 'POST':

		if general_settings_instance:
			general_settings_form = GeneralScheduleSettingsForm(
																request.POST,
																instance = general_settings_instance,
																)
		else:
			general_settings_form = GeneralScheduleSettingsForm(
																request.POST,
																)

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
		if general_settings_form.is_valid():
			obj = general_settings_form.save(commit = False)
			obj.general_setting_user = request.user
			obj.save()


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
	
	'''
		Need to check formsets one by one since it gives you
		[{},{},{}] for formsets with no errors
	'''
	requirement_day_time_errors = False
	for form_errors in employee_requirement_daytime_formset.errors:
		if len(form_errors) > 0:
			requirement_day_time_errors = True
			break;
	
	requirement_date_time_errors = False
	for form_errors in employee_requirement_datetime_formset.errors:
		if len(form_errors) > 0:
			requirement_date_time_errors = True
			break;

	context = {
				'GeneralSettingsForm': general_settings_form,
				'RequirementDayTimeFormSet': employee_requirement_daytime_formset,
				'RequirementDateTimeFormSet': employee_requirement_datetime_formset,
				'RequirementDayTimeFormSetErrors': requirement_day_time_errors,
				'RequirementDateTimeFormSetErrors': requirement_date_time_errors,
				}

	return render(request,template,context)

@login_required
def create_new_employee(request):
	''' Doing some settings based setup'''

	template_redirect = 'OptiSched:dashboard'
	template = 'CreateEmployee.html'
	
	EmployeeRequestDayTimeFormSet = forms.modelformset_factory(
																RequestDayTime,
																form = EmployeeRequestDayTimeForm,
																extra = 5,
																can_delete = True,
																)

	EmployeeRequestDateTimeFormSet = forms.modelformset_factory(
																RequestDateTime,
																form = EmployeeRequestDateTimeForm,
																extra = 5,
																can_delete = True,
																)

	EmployeeEmployeeTypeFormSet = make_EmployeeEmployeeTypeForm(
																request.user,
																2,
																)

	if request.method == 'POST':

		objects_to_save = []
		objects_to_delete = []

		validation_error_found = False

		employee = ""

		employee_info_form = EmployeeInfoForm(request.POST)

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
		if employee_info_form.is_valid():
			employee = Person.objects.create(
												person_user = request.user,
												first_name = employee_info_form.cleaned_data.get('first_name'),
												last_name = employee_info_form.cleaned_data.get('last_name'),
												person_min_hours_per_week = employee_info_form.cleaned_data.get('person_min_hours_per_week'),
												person_max_hours_per_week = employee_info_form.cleaned_data.get('person_max_hours_per_week'),
												person_min_hours_per_shift = employee_info_form.cleaned_data.get('person_min_hours_per_shift'),
												person_max_hours_per_shift = employee_info_form.cleaned_data.get('person_max_hours_per_shift'),
												)
		else:
			validation_error_found = True

		# Request Date times
		if (not validation_error_found
			and employee_request_datetime_formset.is_valid()):

			# Delete
			for request_form in employee_request_datetime_formset.deleted_forms:
				if request_form.instance.id:
					objects_to_delete.append(request_form.instance)

			# Save
			for request_form in employee_request_datetime_formset:

				if not request_form.is_valid():
					validation_error_found = True
					break
				elif (request_form not in employee_request_datetime_formset.deleted_forms
					and request_form.has_changed()):
						obj = request_form.save(commit = False)
						obj.rqst_date_employee = employee
						obj.request_date_time_user = request.user
						objects_to_save.append(obj)
		else:
			validation_error_found = True

		# Request Day Times
		if (not validation_error_found
			and employee_request_daytime_formset.is_valid()):

			# Delete
			for request_form in employee_request_daytime_formset.deleted_forms:
				if request_form.instance.id:
					objects_to_delete.append(request_form.instance)

			# Save
			for request_form in employee_request_daytime_formset:

				if not request_form.is_valid():
					validation_error_found = True
					break
				elif (request_form not in employee_request_daytime_formset.deleted_forms
					and request_form.has_changed()):
						obj = request_form.save(commit = False)
						obj.rqst_day_employee = employee
						obj.request_day_time_user = request.user
						objects_to_save.append(obj)
		else:
				validation_error_found = True

		# Request Day Times
		if (not validation_error_found
			and employee_employeetype_formset.is_valid()):

			# Delete
			for form in employee_employeetype_formset.deleted_forms:
				if form.instance.pk:
					objects_to_delete.append(form.instance)

			# Save
			employee_types = []
			for form in employee_employeetype_formset:

				if form.is_valid():

					if form not in employee_employeetype_formset.deleted_forms:

						if 'pet_employee_type' in form.cleaned_data.keys():
							if form.cleaned_data['pet_employee_type']:

								if form.has_changed():
									obj = form.save(commit = False)
									obj.pet_employee = employee
									obj.person_employee_type_user = request.user
									objects_to_save.append(obj)

								if form.instance.pet_employee_type in employee_types:
									form.add_error('pet_employee_type',"Duplicate Entry")
									validation_error_found = True

								employee_types.append(form.instance.pet_employee_type)
				else:
					validation_error_found = True
		else:
			validation_error_found = True

		if validation_error_found:
			if employee:
				employee.delete()
		else:

			# delete all objects
			for obj in objects_to_delete:
				obj.delete()

			# save all objects
			for obj in objects_to_save:
				obj.save()

			if 'SaveAndDash' in request.POST:
				return HttpResponseRedirect(reverse(template_redirect))
			elif 'SaveAndAnother' in request.POST:

				# reset screen for new employee to be added
				employee_info_form = EmployeeInfoForm()

				employee_request_datetime_formset = EmployeeRequestDateTimeFormSet(
																					prefix='request_date_time',
																					queryset = RequestDateTime.objects.none(),																			
																					)

				employee_request_daytime_formset = EmployeeRequestDayTimeFormSet(
																					prefix='request_day_time',
																					queryset = RequestDayTime.objects.none(),
																					)

				employee_employeetype_formset = EmployeeEmployeeTypeFormSet(
																				prefix='employee_type',
																				queryset = PersonEmployeeType.objects.none(),
																				)
	else:

		employee_info_form = EmployeeInfoForm()

		employee_request_datetime_formset = EmployeeRequestDateTimeFormSet(
																			prefix='request_date_time',
																			queryset = RequestDateTime.objects.none(),																			
																			)

		employee_request_daytime_formset = EmployeeRequestDayTimeFormSet(
																			prefix='request_day_time',
																			queryset = RequestDayTime.objects.none(),
																			)

		employee_employeetype_formset = EmployeeEmployeeTypeFormSet(
																		prefix='employee_type',
																		queryset = PersonEmployeeType.objects.none(),
																		)	

	'''
		Need to check formsets one by one since it gives you
		[{},{},{}] for formsets with no errors
	'''
	request_day_time_errors = False
	for form_errors in employee_request_daytime_formset.errors:
		if len(form_errors) > 0:
			request_day_time_errors = True
			break;
	
	request_date_time_errors = False
	for form_errors in employee_request_datetime_formset.errors:
		if len(form_errors) > 0:
			request_date_time_errors = True
			break;
	
	employee_type_errors = False
	for form_errors in employee_employeetype_formset.errors:
		if len(form_errors) > 0:
			employee_type_errors = True
			break;


	context = {
				'EmployeeInfoForm': employee_info_form,
				'EmployeeRequestDayTimeFormSet': employee_request_daytime_formset,
				'EmployeeRequestDateTimeFormSet': employee_request_datetime_formset,
				'EmployeeEmployeeTypeFormSet': employee_employeetype_formset,
				'EmployeeRequestDayTimeFormSetErrors': request_day_time_errors,
				'EmployeeRequestDateTimeFormSetErrors': request_date_time_errors,
				'EmployeeEmployeeTypeFormSetErrors': employee_type_errors,
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
	template_redirect_dashboard = 'OptiSched:dashboard'
	template_redirect_employee_list = 'OptiSched:EmployeeList'
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
																).order_by(
																			'pet_employee_type',
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

		objects_to_save = []
		objects_to_delete = []

		validation_error_found = False

		employee_info_form = EmployeeInfoForm(
												request.POST,
												instance = employee,
												)

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
		if employee_info_form.is_valid():
			obj = employee_info_form.save(commit = False)
			obj.person_user = request.user
			#obj.save()
			objects_to_save.append(obj)
		else:
			validation_error_found = True

		# Request Date times
		if (not validation_error_found
			and employee_request_datetime_formset.is_valid()):

			# Delete
			for request_form in employee_request_datetime_formset.deleted_forms:
				if request_form.instance.id:
					#request_form.instance.delete()
					objects_to_delete.append(request_form.instance)

			# Save
			for request_form in employee_request_datetime_formset:

				if not request_form.is_valid():
					validation_error_found = True
					break
				elif (request_form not in employee_request_datetime_formset.deleted_forms
					and request_form.has_changed()):
						obj = request_form.save(commit = False)
						obj.rqst_date_employee = employee
						obj.request_date_time_user = request.user
						#obj.save()
						objects_to_save.append(obj)
		else:
			validation_error_found = True

		# Request Day Times
		if (not validation_error_found
			and employee_request_daytime_formset.is_valid()):

			# Delete
			for request_form in employee_request_daytime_formset.deleted_forms:
				if request_form.instance.id:
					#request_form.instance.delete()
					objects_to_delete.append(request_form.instance)

			# Save
			for request_form in employee_request_daytime_formset:

				if not request_form.is_valid():
					validation_error_found = True
					break
				elif (request_form not in employee_request_daytime_formset.deleted_forms
					and request_form.has_changed()):
						obj = request_form.save(commit = False)
						obj.rqst_day_employee = employee
						obj.request_day_time_user = request.user
						#obj.save()
						objects_to_save.append(obj)
		else:
				validation_error_found = True

		# Request Day Times
		if (not validation_error_found
			and employee_employeetype_formset.is_valid()):

			# Delete
			for form in employee_employeetype_formset.deleted_forms:
				if form.instance.pk:
					#form.instance.delete()
					objects_to_delete.append(form.instance)

			# Save
			employee_types = []
			for form in employee_employeetype_formset:

				if form.is_valid():

					if form not in employee_employeetype_formset.deleted_forms:

						if 'pet_employee_type' in form.cleaned_data.keys():
							if form.cleaned_data['pet_employee_type']:

								if form.has_changed():
									obj = form.save(commit = False)
									obj.pet_employee = employee
									obj.person_employee_type_user = request.user
									objects_to_save.append(obj)

								if form.instance.pet_employee_type in employee_types:
									form.add_error('pet_employee_type',"Duplicate Entry")
									validation_error_found = True

								employee_types.append(form.instance.pet_employee_type)
				else:
					validation_error_found = True
		else:
			validation_error_found = True

		# file objects if everything okay
		if not validation_error_found:
				
			# delete all objects
			for obj in objects_to_delete:
				obj.delete()

			# save all objects
			for obj in objects_to_save:
				obj.save()

			if 'SaveAndDashboard' in request.POST:
				return HttpResponseRedirect(reverse(template_redirect_dashboard))
			elif 'SaveAndEmployeeList' in request.POST:
				return HttpResponseRedirect(reverse(template_redirect_employee_list))
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
	'''
		Need to check formsets one by one since it gives you
		[{},{},{}] for formsets with no errors
	'''
	request_day_time_errors = False
	for form_errors in employee_request_daytime_formset.errors:
		if len(form_errors) > 0:
			request_day_time_errors = True
			break;
	
	request_date_time_errors = False
	for form_errors in employee_request_datetime_formset.errors:
		if len(form_errors) > 0:
			request_date_time_errors = True
			break;
	
	employee_type_errors = False
	for form_errors in employee_employeetype_formset.errors:
		if len(form_errors) > 0:
			employee_type_errors = True
			break;

	context = {
				'IdentifiedEmployee': employee,
				'EmployeeInfoForm':employee_info_form,
				'EmployeeRequestDayTimeFormSet': employee_request_daytime_formset,
				'EmployeeRequestDateTimeFormSet': employee_request_datetime_formset,
				'EmployeeEmployeeTypeFormSet': employee_employeetype_formset,
				'EmployeeRequestDayTimeFormSetErrors': request_day_time_errors,
				'EmployeeRequestDateTimeFormSetErrors': request_date_time_errors,
				'EmployeeEmployeeTypeFormSetErrors': employee_type_errors,
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
			timeslice = ""

			new_date = date_external = form.cleaned_data['f_date']
			start_time = form.cleaned_data.get('f_start_time')
			end_time = form.cleaned_data.get('f_end_time')

			request.session['DATE_STR'] = new_date.isoformat()

			try:
				general_settings_instance = GeneralSetting.objects.get(
																		general_setting_user = request.user,
																		)

				timeslice = general_settings_instance.general_setting_time_slice
			except GeneralSetting.DoesNotExist:
				"nothing to do"

			if not timeslice:
				timeslice = TIMESLICE

			create_from_scratch = False
			if 'NewWorkday' in request.POST:
				create_from_scratch = True

			a_workday = Workday.CreateDay(
											user = request.user,
											date = new_date,
											date_start_time = start_time,
											date_end_time = end_time,
											timeslice = timeslice,
											create_from_scratch = create_from_scratch,
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

			timeslice = ""

			from_date = form.cleaned_data.get('f_from_date')
			thru_date = form.cleaned_data.get('f_thru_date')
			#from_date_obj = dt.datetime.strptime(from_date, "%Y-%m-%d").date()
			#thru_date_obj = dt.datetime.strptime(thru_date, "%Y-%m-%d").date()

			start_time = form.cleaned_data.get('f_start_time')
			end_time = form.cleaned_data.get('f_end_time')

			#start_time_obj = dt.datetime.strptime(start_time, "%H:%M:%S").time()
			#end_time_obj = dt.datetime.strptime(end_time, "%H:%M:%S").time()

			try:
				general_settings_instance = GeneralSetting.objects.get(
																		general_setting_user = request.user,
																		)

				timeslice = general_settings_instance.general_setting_time_slice
			except GeneralSetting.DoesNotExist:
				"nothing to do"

			if not timeslice:
				timeslice = TIMESLICE



			create_from_scratch = False
			if 'NewSpan' in request.POST:
				create_from_scratch = True


			all_dates = []

			# create and populate dates
			for single_date in daterange(from_date,thru_date):

				a_workday = Workday.CreateDay(
												user = request.user,
												date = single_date,
												date_start_time = start_time,
												date_end_time = end_time,
												timeslice = timeslice,
												create_from_scratch = create_from_scratch,
												)
				a_workday.GenerateShifts()

				all_dates.append(a_workday)
			
			# save all dates
			for workday in all_dates:
				workday.Save()

			request.session['DATE_STR'] = from_date.isoformat()
			return HttpResponseRedirect(reverse(template_redirect))
	else:        

		form = CreateDateSpanForm()

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
		elif 'DATE_STR' in request.session:
			date = request.session['DATE_STR'] 
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

				errors_per_date = EmployeeTypeShiftError.objects.filter(
																			employee_type_shift_error_user = request.user,
																			error_date = work_day,
																			)
				
				context = {
							'NavDateForm': form,
							'work_day_display': work_day.date_display,
	   						'shifts': shifts_per_date,
	   						'date_errors':errors_per_date,
							'Error': "No shifts for the specified date",
	   					}
			except ObjectDoesNotExist:
				context = {
						'NavDateForm': form,
						'Error': "No workday for the specified date",
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





