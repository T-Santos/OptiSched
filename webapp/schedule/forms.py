from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, ButtonHolder, Submit, MultiField, HTML,Field

from .models import *

import datetime as dt
import pdb

class GeneralScheduleSettingsForm(forms.ModelForm):

	class Meta:
			model = GeneralSetting
			#fields = '__all__'
			exclude = ['general_setting_user']

class NavDateForm(forms.Form):
	# get the latest date in the database and increase it by 1 otherwise use today's date
		
	try:
    		#Date = Date.objects.get(date=dt.datetime.today().strftime("%Y-%m-%d"))
		#navdate = forms.DateField(initial = Date)
		# Date = most recent in db
		navdate = forms.DateField(initial = dt.datetime.today().strftime("%Y-%m-%d"))
	except ObjectDoesNotExist:
    		navdate = forms.DateField()

class CreateDateForm(forms.Form):
	# get the latest date in the database and increase it by 1 otherwise use today's date
	f_date = forms.DateField(initial = dt.datetime.today().strftime("%Y-%m-%d"))

	f_start_time = forms.TimeField(input_formats=settings.TIME_INPUT_FORMATS)
	f_end_time = forms.TimeField(input_formats=settings.TIME_INPUT_FORMATS)

	def clean(self):
		cleaned_data = super(CreateDateForm,self).clean()

		start_time = cleaned_data.get('f_start_time',False)
		end_time = cleaned_data.get('f_end_time',False)

		if start_time == datetime.time(0,0,0):
			"Do nothing" 
		elif not start_time:
			msg = "Start Time is required"
			raise forms.ValidationError(msg)

		if end_time == datetime.time(0,0,0):
			"Do Nothing"
		elif not end_time:
			msg = "End Time is required"
			raise forms.ValidationError(msg)
		
		if (start_time == datetime.time(0,0,0)
			and end_time == datetime.time(0,0,0)):
			"Do nothing"
		elif not start_time < end_time:
			if not end_time == datetime.time(0,0,0):
				msg = "End Time must fall after Start Time"
				raise forms.ValidationError(msg)

class CreateDateSpanForm(forms.Form):

	f_from_date = forms.DateField()
	f_thru_date = forms.DateField()

	f_start_time = forms.TimeField(input_formats=settings.TIME_INPUT_FORMATS)
	f_end_time = forms.TimeField(input_formats=settings.TIME_INPUT_FORMATS)

	def clean(self):
		cleaned_data = super(CreateDateSpanForm,self).clean()

		from_date = cleaned_data.get('f_from_date')
		thru_date = cleaned_data.get('f_thru_date')

		start_time = cleaned_data.get('f_start_time')
		end_time = cleaned_data.get('f_end_time')

		if not from_date:
			msg = "From Date is required"
			self.add_error('f_from_date',msg)
		
		if not thru_date:
			msg = "Thru Date is required"
			self.add_error('f_thru_date',msg)

		if not from_date <= thru_date:
			msg = "From Date must fall before Thru Date"
			raise forms.ValidationError(msg)

		# Time Validation could be consolidated with create date time 
		# validatior	
		if start_time == datetime.time(0,0,0):
			"Do nothing" 
		elif not start_time:
			msg = "Start Time is required"
			raise forms.ValidationError(msg)

		if end_time == datetime.time(0,0,0):
			"Do Nothing"
		elif not end_time:
			msg = "End Time is required"
			raise forms.ValidationError(msg)
		
		if (start_time == datetime.time(0,0,0)
			and end_time == datetime.time(0,0,0)):
			"Do nothing"
		elif not start_time < end_time:
			if not end_time == datetime.time(0,0,0):
				msg = "End Time must fall after Start Time"
				raise forms.ValidationError(msg)

class EmployeeInfoForm(forms.ModelForm):
	class Meta:
			model = Person
			#fields = '__all__'
			exclude = ['person_user']

class EmployeeRequestDayTimeForm(forms.ModelForm):

	helper = FormHelper()
	helper.form_tag = False

	helper.layout = Layout(
							Div(
								Div(
									Div(
										Field(
												'rqst_day_type',
												),
										css_class = 'col-lg-3',
										),
									Div(
										Field(
												'day_of_week',
												),
										css_class = 'col-lg-3',
										),
									Div(
										Field(
												'rqst_day_start_time',
												css_class = 'time',
												),
										css_class = 'col-lg-2',
										), 
									Div(
										Field(
												'rqst_day_end_time',
												css_class = 'time',
												),
										css_class = 'col-lg-2',
										),
									Div(
										'DELETE',
										css_class = 'col-lg-2',
										style = 'padding-top: 20px'
										),
									css_class = "row",
									),
								css_class="dynamic-form",
								),
							)
	
	class Meta:
			model = RequestDayTime
			fields = [
						'rqst_day_type',
						'day_of_week',
						'rqst_day_start_time',
						'rqst_day_end_time',
					]

class EmployeeRequestDateTimeForm(forms.ModelForm):

	helper = FormHelper()
	helper.form_tag = False
		
	helper.layout = Layout(
							Div(
								Div(
									Div(
										Field(
												'rqst_date_type',
												),
										css_class = 'col-lg-3',
										),
									Div(
										Field(
												'rqst_date_date',
												css_class = 'date',
												),
										css_class = 'col-lg-3',
										),
									Div(
										Field(
												'rqst_date_start_time',
												css_class = 'time',
												),
										css_class = 'col-lg-2',
										), 
									Div(
										Field(
												'rqst_date_end_time',
												css_class = 'time',
												),
										css_class = 'col-lg-2',
										),
									Div(
										'DELETE',
										css_class = 'col-lg-2',
										style = 'padding-top: 20px'
										),
									css_class = "row",
									),
								css_class="dynamic-form",
								),
							)
	
	class Meta:
			model = RequestDateTime
			fields = [
						'rqst_date_type',
						'rqst_date_date',
						'rqst_date_start_time',
						'rqst_date_end_time',
					]

def make_EmployeeEmployeeTypeForm(
									user,
									extra,
									):
	class EmployeeEmployeeTypeForm(forms.ModelForm):

		helper = FormHelper()
		helper.form_tag = False
		#helper.form_show_labels = False
		
		helper.layout = Layout(
								Div(
									Div(
										Div(
											Field(
													'pet_employee_type',
													),
											css_class = 'col-lg-10',
											),
										Div(
											Field(
													'DELETE',
													),
											css_class = 'col-lg-2',
											),
										css_class = "row",
										),
									css_class="dynamic-form",
									),
								)

		def __init__(self,*args, **kwargs):
			super(EmployeeEmployeeTypeForm, self).__init__(*args, **kwargs)
			self.fields['pet_employee_type'].label = False
			self.fields['pet_employee_type'].queryset = EmployeeType.objects.filter(
																						employee_type_user = user,
																						)

		class Meta:
				model = PersonEmployeeType
				# if i do __all__ here it barks when i go to save saying its not valid look into clean_data
				fields = ['pet_employee_type',]

	return forms.modelformset_factory(
										PersonEmployeeType,
										form = EmployeeEmployeeTypeForm,
										extra = extra,
										can_delete = True,
																)

class EmployeeTypesForm(forms.ModelForm):

	helper = FormHelper()
	helper.form_tag = False
	#helper.form_show_labels = False
	helper.layout = Layout(
							Div(
								Div(
									Div(
										Field(
												'et_type',
												placeholder = 'Position',
												),
										css_class = 'col-lg-10',
										),
									Div(
										'DELETE',
										css_class = 'col-lg-2',
										),
									css_class = "row",
									),
								css_class="dynamic-form",
								),
							)

	def __init__(self, *args, **kwargs):
		super(EmployeeTypesForm, self).__init__(*args, **kwargs)
		self.fields['et_type'].label = False

	class Meta:
			model = EmployeeType
			#fields = '__all__'
			fields = ['et_type',]

def make_RequirementTimeForm(
								user,
								extra,
								):
	class RequirementTimeForm(forms.ModelForm):

		helper = FormHelper()
		helper.form_tag = False
		helper.layout = Layout(
								Div(
									Div(
										Div(
											Field(
													'rqmt_start_time',
													css_class = 'time',
													),
											css_class = 'col-lg-3',
											),
										Div(
											Field(
													'rqmt_employee_count',
													),
											css_class = 'col-lg-3',
											), 
										Div(
											Field(
													'rqmt_employee_type',
													),
											css_class = 'col-lg-3',
											),
										Div(
											'DELETE',
											css_class = 'col-lg-3',
											style = 'padding-top: 20px'
											),
										css_class = "row",
										),
									css_class="dynamic-form",
									),
								)
		
		class Meta:
				model = RequirementTime
				fields = [
							'rqmt_start_time',
							'rqmt_employee_type',
							'rqmt_employee_count',
						]

		def __init__(self, *args, **kwargs):
			super(RequirementTimeForm, self).__init__(*args, **kwargs)
			self.fields['rqmt_start_time'].label = 'Effective'
			self.fields['rqmt_employee_type'].label = 'Position'
			self.fields['rqmt_employee_type'].queryset = EmployeeType.objects.filter(
																						employee_type_user = user,
																						)
			self.fields['rqmt_employee_count'].label = 'Count'

	return forms.modelformset_factory(
										RequirementTime,
										form = RequirementTimeForm,
										extra = extra,
										can_delete = True,
										)

def make_RequirementDayTimeForm(
								user,
								extra,
								):
	class RequirementDayTimeForm(forms.ModelForm):

		helper = FormHelper()
		helper.form_tag = False
		helper.layout = Layout(
								Div(
									Div(
										Div(
											Field(
													'day_of_week',
													),
											css_class = 'col-lg-3',
											),
										Div(
											Field(
													'rqmt_day_start_time',
													css_class = 'time',
													),
											css_class = 'col-lg-2',
											),
										Div(
											Field(
													'rqmt_day_employee_count',
													),
											css_class = 'col-lg-2',
											), 
										Div(
											Field(
													'rqmt_day_employee_type',
													),
											css_class = 'col-lg-3',
											),
										Div(
											'DELETE',
											css_class = 'col-lg-2',
											style = 'padding-top: 20px'
											),
										css_class = "row",
										),
									css_class="dynamic-form",
									),
								)
		
		class Meta:
				model = RequirementDayTime
				fields = [
							'day_of_week',
							'rqmt_day_start_time',
							'rqmt_day_employee_type',
							'rqmt_day_employee_count',
						]

		def __init__(self, *args, **kwargs):
			super(RequirementDayTimeForm, self).__init__(*args, **kwargs)
			self.fields['day_of_week'].label = 'Day of week'
			self.fields['rqmt_day_start_time'].label = 'Effective'
			self.fields['rqmt_day_employee_type'].label = 'Position'
			self.fields['rqmt_day_employee_type'].queryset = EmployeeType.objects.filter(
																							employee_type_user = user,
																							)
			self.fields['rqmt_day_employee_count'].label = 'Count'

	return forms.modelformset_factory(
										RequirementDayTime,
										form = RequirementDayTimeForm,
										extra = extra,
										can_delete = True,
										)

def make_RequirementDateTimeForm(user,extra,):
	class RequirementDateTimeForm(forms.ModelForm):

		helper = FormHelper()
		helper.form_tag = False
		
		helper.layout = Layout(
								Div(
									Div(
										Div(
											Field(
													'rqmt_date_date',
													css_class = 'date',
													),
											css_class = 'col-lg-3',
											),
										Div(
											Field(
													'rqmt_date_time',
													css_class = 'time',
													),
											css_class = 'col-lg-3',
											),
										Div(
											Field(
													'rqmt_date_employee_count',
													),
											css_class = 'col-lg-2',
											), 
										Div(
											Field(
													'rqmt_date_employee_type',
													),
											css_class = 'col-lg-2',
											),
										Div(
											'DELETE',
											css_class = 'col-lg-2',
											style = 'padding-top: 20px'
											),
										css_class = "row",
										),
									css_class="dynamic-form",
									),
								)
		
		class Meta:
				model = RequirementDateTime
				fields = [
							'rqmt_date_date',
							'rqmt_date_time',
							'rqmt_date_employee_count',
							'rqmt_date_employee_type',
						]

		def __init__(self,*args, **kwargs):
			super(RequirementDateTimeForm, self).__init__(*args, **kwargs)
			self.fields['rqmt_date_employee_count'].label = 'Count'
			self.fields['rqmt_date_employee_type'].label = 'Position'
			self.fields['rqmt_date_employee_type'].queryset = EmployeeType.objects.filter(
																							employee_type_user = user,
																							)

	return forms.modelformset_factory(
										RequirementDateTime,
										form = RequirementDateTimeForm,
										extra = extra,
										can_delete = True,
										)
