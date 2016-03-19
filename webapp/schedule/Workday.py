import datetime as dt
import time
import random
import pdb
import copy
from collections import namedtuple

from .models import *
import ScheduleDateTimeUtilities

class CreateDay(object):
    ''' 
        Class data members (persist across instances and are not specific to an individual WorkDay instance)
    '''

    ''' 
    *********************************
            CTOR
    *********************************
    '''
    def __init__(
                self,
                user,
                date,
                date_start_time = datetime.time(0,0,0),
                date_end_time = datetime.time(0,0,0),
                timeslice = 5,
                ):
        '''
        ***********************************
            instance data members
        ***********************************
            should have underscore (_) prefix if private
            
            date_model_obj              : the Date object created based off of the model
            employee_type_shift_errors          : list of all notifications generated when creating a work day

            shift_all                   : list of all Shift objects that are done or in progress
            shift_active                : list of Shift objects that are currently in progress

            time_slice                  : int for how many minutes in a time slice say 5 minute increments
            time_slice_total            : int for the total number of time slices in the given day

            employee_all                : QuerySet of all Person objects in the DB
            employees_already_working   : list of Person objects that either cannot work the current time slice because they are already working


        ''' 
        self.TIMESLICE = timeslice

        self.user = user

        # Round start and end time to nearest TIMESLICE
        start_datetime = dt.datetime.combine(date,date_start_time)
        start_datetime_floor = ScheduleDateTimeUtilities.FloorDatetime(start_datetime,self.TIMESLICE)
        date_start_time = start_datetime_floor.time()

        end_datetime = dt.datetime.combine(date,date_end_time)
        end_datetime_ceiling = ScheduleDateTimeUtilities.CeilingDatetime(end_datetime,self.TIMESLICE)
        date_end_time = end_datetime_ceiling.time()

        # TODO: we might want to see if a date object already exists before creating one
        self.date_model_obj =  Date(
                                    date_user = self.user,
                                    date=date,
                                    day_start_time=date_start_time,
                                    day_end_time=date_end_time,
                                    )

        self.shift_all = self.GetAllShifts()
        self.shift_active = []

        self.time_slice = self.TIMESLICE
        self.time_slice_total = self.GetTimeSliceTotal()

        self.employee_all = Person.objects.filter(
                                                    person_user = self.user,
                                                    )

        # these should all be private setters
        self.employees_already_working = self.GetAlreadyWorkingEmployees()

        # maybe should check to see if there are any existing notifications...
        # do we just delete all and start from scratch each time?
        self.employee_type_shift_errors = []

    '''
    ********************************
            Methods
    ********************************
        previx name with underscores (__) to mark it as being private if needed
    '''

    def Save(self):
        '''
            Save all of the objects that were created and need to be filed to the DB
        '''
        self.date_model_obj.save()

        for shift in self.shift_all:
            shift.save()

        # Delete any old errors before saving the new ones
        EmployeeTypeShiftError.objects.filter(
                                                employee_type_shift_error_user = self.user,
                                                error_date = self.date_model_obj
                                                ).delete()

        for notification in self.employee_type_shift_errors:
            notification.save()

    def GetTimeSliceTotal(self):
        '''
        Returns: Int for the Total number of time slices in a given day with a start time and an end time

        '''

        start_mins = ((self.date_model_obj.day_start_time.hour * 60) + self.date_model_obj.day_start_time.minute)

        if self.date_model_obj.day_end_time.hour == 0:
            end_hour = 24
        else:
            end_hour = self.date_model_obj.day_end_time.hour
        end_mins = ((end_hour * 60) + self.date_model_obj.day_end_time.minute)

        #return (((end_mins - start_mins) / self.time_slice) - 1)
        return (((end_mins - start_mins) / self.time_slice))

    def GetAllShifts(self):
        '''
            Get all the shifts that have already been saved for a given date
        '''
        shift_all = []

        shifts = Shift.objects.filter(
                                        shift_user = self.user,
                                        shift_date = self.date_model_obj,
                                        )
        
        for shift in shifts:
            shift_all.append(shift)

        return shift_all

    def GetAlreadyWorkingEmployees(self):
        '''
            Get all employees that have saved shifts
        '''
        already_working_employees = []

        for saved_shift in self.shift_all:
            already_working_employees.append(saved_shift.employee)

        return already_working_employees

    def GenerateShifts(self):
        '''
            Called to generate shifts for a Workday


            employee_types_needed_for_timeslice :   List of EmployeeType objects or 
                                                    False if none are needed in a give timeslice
            Employee                            :   namedtuple structure
                                                    person : Person Object
                                                    type   : EmployeeType Object
            time_slice                          :   counter for which time slice we are processing in the given day
            time_slice_datetime                 :   the counter and workday start time converted into a datetime object
        '''
        employee_types_needed_for_timeslice = []
        
        NewEmployee = namedtuple('NewEmployee', 'person type')

        # for each time slice in the workday
        for timeslice in range(self.time_slice_total):

            time_slice_datetime = self.ConvertTimeSliceToDateTime(timeslice)
            
            # Assume there are shifts to be filled in the timeslice
            while True:

                # Since we need shifts, determine the employee types that are needed
                # to fill the shifts needed
                # List[:] = [] is used to reset the list each iteration
                # because of the new shifts created we want to update to reflect them
                employee_types_needed_for_timeslice[:] = []
                employee_types_needed_for_timeslice = self.GetEmployeeTypesNeededForTimeSlice(time_slice_datetime)

                if not employee_types_needed_for_timeslice:
                    # no more shifts needed for this timeslice, move on
                    break;
                else:
                    # get employee and type 
                    employee_new = NewEmployee._make(
                                                        self.GetNewEmployee(
                                                                                employee_types_needed_for_timeslice,
                                                                                time_slice_datetime,
                                                                            )
                                                        )
                    # if there isnt an employee to fill a shift log an error an break
                    if not employee_new.person:
                        # log error
                        for employee_type,type_count in employee_types_needed_for_timeslice:
                            date_notification = EmployeeTypeShiftError(
                                                                        employee_type_shift_error_user = self.user,
                                                                        error_date = self.date_model_obj,
                                                                        error_time = time_slice_datetime.time(),
                                                                        error_emp_type = employee_type
                                                                    )
                            self.employee_type_shift_errors.append(date_notification)
                        break;
                    else:
                        # create the shift object
                        shift_new = Shift(
                                            shift_user = self.user,
                                            shift_date = self.date_model_obj,
                                            employee = employee_new.person,
                                            shift_employee_type = employee_new.type
                                            )
            
                        shift_new.start_time = time_slice_datetime.time()
                        #shift_new.end_time = time_slice_datetime.time()

                        # add new shift object to all and to active lists
                        self.shift_active.append(shift_new)
                        self.shift_all.append(shift_new)

                        # add employee to already working list
                        self.employees_already_working.append(employee_new.person)
            '''
                done with creating new shifts
            '''
            # update potential end time
            time_slice_datetime_endtime = self.ConvertTimeSliceToDateTime((timeslice+1))

            # update the end times for each active shift
            for active_shift in self.shift_active:
                active_shift.end_time = time_slice_datetime_endtime

            # remove any shifts that should be done as of now  
            self.shift_active = self.RemoveActiveShifts(time_slice_datetime_endtime)

    def GetEmployeeTypesNeededForTimeSlice(self,datetime):
        '''
            given a datetime determine what employee types are needed to fill shifts
        '''

        # get dict of requirement types keyed by the type of employee (manager, cook, eye dr., etc)
        employee_type_requirements = {}
        employee_type_requirements = self.GetEmployeeTypeRequirements(datetime) 

        # final list of employee type requirements  
        employee_type_requirements_needed = []

        # make sure we have at least some type of requirement? 
        # if not are they only a morning, 6-11 everybody go home 5-12 type of business
        if ( not(employee_type_requirements) ):
            # maybe not log error since employees dont start until 8 and the day starts at 0:00 for whatever reason
            "Log as an error"
        else:

            if( not(self.shift_active) ):
                
                # if there are no active shifts, we need to fill all spots defined by the requirements
                # [0] is the most relevant time since we append them [most,relevant,to,least,relevant]
                for temp_employee_type, temp_employee_requirement_count_list in employee_type_requirements.items():
                    employee_type_requirements_needed.append(
                                                                [
                                                                    EmployeeType.objects.get(
                                                                                                employee_type_user = self.user,
                                                                                                pk = temp_employee_type,
                                                                                                ),
                                                                    temp_employee_requirement_count_list[0]
                                                                    ]
                                                                )
            else:
                # get the counts for all the active working employee types
                active_type_counts = {}
                for active_shift in self.shift_active:
                    active_type_counts[active_shift.shift_employee_type.et_type] = active_type_counts.get(active_shift.shift_employee_type.et_type,0) + 1

                # for all the requirements, if they aren't filled make sure we return that we need them
                for temp_employee_type, temp_employee_requirement_count_list in employee_type_requirements.items():

                    if( active_type_counts.get(temp_employee_type,0) < temp_employee_requirement_count_list[0] ):
                        employee_type_requirements_needed.append(
                                                                    [
                                                                        EmployeeType.objects.get(
                                                                                                    employee_type_user = self.user,
                                                                                                    pk = temp_employee_type,
                                                                                                    ),
                                                                        temp_employee_requirement_count_list[0]
                                                                        ]
                                                                    )

        return employee_type_requirements_needed

    def GetEmployeeTypeRequirements(self,datetime):

        # form current datetime 
        now = datetime

        # form beginning of the day
        begin_of_day = dt.datetime.combine(datetime.date(),self.date_model_obj.day_start_time)
        
        #-----------------------------
        # get employee requirements
        # we get the request from most recent (across all types) to least recent
        # and then later sort them out by type. For each type [0] will be the most 
        # recent since the most recent gets put in first

        # given the current date and time see if there are any
        # override specific datetime requirements
        emp_req_ovrs = RequirementDateTime.objects.filter(
                                                            requirement_date_time_user = self.user,
                                                            rqmt_date_date__gte = begin_of_day.date(),
                                                            rqmt_date_date__lte = now.date(),
                                                            rqmt_date_time__gte = begin_of_day.time(),
                                                            rqmt_date_time__lte = now.time(),
                                                            ).order_by(
                                                                        '-rqmt_date_date',
                                                                        '-rqmt_date_time'
                                                                        )

        # if there are no employee requirement overrides, check for requirements for the 
        # given day of the week and time
        if (not emp_req_ovrs):
            emp_reqs = RequirementDayTime.objects.filter(
                                                            requirement_day_time_user = self.user,
                                                            day_of_week = self.date_model_obj.date.weekday(),
                                                            rqmt_day_start_time__lte = now
                                                            ).order_by(
                                                                        '-rqmt_day_start_time')

        # Make a map/dictionary of employee type reqirements and types needed checking
        '''
        { Managers , [count 1,count 2] }
        { Cooks    , [count 1,count 2] }
        '''
        employee_type_requirements = {}
            
        # Divvy the requirements out by employee type
        if emp_req_ovrs:
            for emp_req_ovr in emp_req_ovrs:
                    if emp_req_ovr.rqmt_date_employee_type.et_type in employee_type_requirements:
                        # append the new number to the existing array at this slot
                        employee_type_requirements[emp_req_ovr.rqmt_date_employee_type.et_type].append(emp_req_ovr.rqmt_date_employee_count)
                    else:
                        # create a new array in this slot
                        employee_type_requirements[emp_req_ovr.rqmt_date_requirement.et_type] = [emp_req_ovr.rqmt_date_employee_count]
        elif emp_reqs:
            for emp_req in emp_reqs:
                    if emp_req.rqmt_day_employee_type.et_type in employee_type_requirements:
                        # append the new number to the existing array at this slot
                        employee_type_requirements[emp_req.rqmt_day_employee_type.et_type].append(emp_req.rqmt_day_employee_count)
                    else:
                        # create a new array in this slot
                        employee_type_requirements[emp_req.rqmt_day_employee_type.et_type] = [emp_req.rqmt_day_employee_count]


        return employee_type_requirements

    def GetNewEmployee(self,emp_types_needed,datetime):
        #------
        unavailable_workers = self.employees_already_working

        year_num = self.date_model_obj.date.year
        week_num = self.date_model_obj.week()
        
        # get all employees
        qs_all_employees = self.employee_all
        available_employees = []

        # get all available employees
        for emp in qs_all_employees:
            if not emp in unavailable_workers:
                available_employees.append(emp)

        # get just the employee types needed    
        temp_emp_types_needed = []
        for emp_type,type_count in emp_types_needed:
            temp_emp_types_needed.append(emp_type)

        
        # ***************************************************************
        # Need to weed out all available employees that are not qualified
        # to work roles for shifts that need to be filled
        # someone who is only a cook cannot fill a manger's shift

        temp_available_employees = []
        temp_available_employees[:] = []
        temp_available_employees = copy.deepcopy(available_employees)

        for available_employee in temp_available_employees:
            
            temp_person_employee_types = []     
            temp_person_employee_types = PersonEmployeeType.objects.filter(
                                                                            person_employee_type_user = self.user,
                                                                            pet_employee = available_employee,
                                                                            )
            
            temp_employee_types = [] 
            for temp_person_employee_type in temp_person_employee_types:
                temp_employee_types.append(temp_person_employee_type.pet_employee_type)
            
            #-----------------------
            # check if at least one type exists in each list
            temp_et_intersect = []
            temp_et_intersect = list(
                                        set.intersection(
                                                            set(temp_employee_types),
                                                            set(temp_emp_types_needed)
                                                            )
                                        )
            
            if not temp_et_intersect:
                available_employees.remove(available_employee)

            #-------------------------
            # check to see if the available employee has already worked enough hours for a full week
            week_dates = namedtuple('week_dates', ['start_date','end_date'])
            week_dates = ScheduleDateTimeUtilities.get_dates_from_week(int(year_num),int(week_num))

            temp_emp_existing_shifts_in_week = Shift.objects.filter(
                                                                    shift_user = self.user,
                                                                    shift_date__gte = week_dates[0],
                                                                    shift_date__lte = week_dates[1],
                                                                    employee = available_employee.id)
            hours_worked_in_week = 0
            for existing_shift in temp_emp_existing_shifts_in_week:
                hours_worked_in_week += existing_shift.hours()

            # if the employee has worked total hours per week; remove them
            if (hours_worked_in_week >= available_employee.person_max_hours_per_week):
                if ( available_employee in available_employees):
                    available_employees.remove(available_employee)
            # if an employee's hours left to work in a week is less than a minimum shift; remove them
            elif (available_employee.person_min_hours_per_shift > (available_employee.person_max_hours_per_week - hours_worked_in_week) ):
                if ( available_employee in available_employees):
                    available_employees.remove(available_employee)
            # Remove available employees who are available to work based on hours left in the week
            # but have a restriction coming up in the same day that is sooner than
            # a minimum shift. 
            # For example, the current hour is 10 they can't work at 12 or later and min shift = 4hrs
            elif( self.HoursUntilCantWork(available_employee,datetime) < available_employee.person_min_hours_per_shift ):
                if ( available_employee in available_employees):
                    available_employees.remove(available_employee)
            
        # Get all DateTime requests that encompass the current time
        # and for only potential new employees
        qs_all_datetime_requests = RequestDateTime.objects.filter(
                                                                    request_date_time_user = self.user,
                                                                    rqst_date_date = datetime.date(),
                                                                    rqst_date_start_time__lte = datetime.time(),
                                                                    rqst_date_end_time__gte = datetime.time()
                                                                ).exclude(
                                                                            rqst_date_employee__in = unavailable_workers
                                                                            )
        # Get all DayTime requests that encompass the current time
        # and for only potential new employees                                                                
        qs_all_daytime_requests = RequestDayTime.objects.filter(
                                                                    request_day_time_user = self.user,
                                                                    day_of_week = self.date_model_obj.date.weekday(),
                                                                    rqst_day_start_time__lte = datetime.time(),
                                                                    rqst_day_end_time__gte = datetime.time()
                                                                    ).exclude(
                                                                                rqst_day_employee__in = unavailable_workers
                                                                                )

        # TODO Make this a dictionary/map
        all_datetime_vacation = []
        all_datetime_sick = []
        all_datetime_preferred = []
        all_datetime_skip = []

        # group them into their different types
        for one_request in qs_all_datetime_requests:
            if (one_request.rqst_date_type == one_request.VACATION):
                all_datetime_vacation.append(one_request)
            elif (one_request.rqst_date_type == one_request.SICK):
                all_datetime_sick.append(one_request)
            elif (one_request.rqst_date_type == one_request.PREFERRED):
                all_datetime_preferred.append(one_request)
            elif (one_request.rqst_date_type == one_request.SKIP):
                all_datetime_skip.append(one_request)

        all_daytime_preferred = []
        all_daytime_skip = []

        # group them into their different types
        for one_request in qs_all_daytime_requests:
            if (one_request.rqst_day_type == one_request.PREFERRED):
                all_daytime_preferred.append(one_request)
            elif (one_request.rqst_day_type == one_request.SKIP):
                all_daytime_skip.append(one_request)

        # ****************************************************************************
        # *** remove all employees from main list that are in cannot work requests ***
        # TODO: Maybe dont need this because we get rid of them based on future even
        
        # Skip requests (cannot work this day)
        if all_datetime_skip:
            for request in all_datetime_skip:
                if request.rqst_date_employee in available_employees:
                    available_employees.remove(request.rqst_date_employee)
        if all_daytime_skip:
            for request in all_daytime_skip:
                if request.rqst_day_employee in available_employees:
                    available_employees.remove(request.rqst_day_employee)

        # Sick requests (im sick or am going to be sick potential dr visit)
        if all_datetime_sick:
            for sick_request in all_datetime_sick:
                if sick_request.rqst_date_employee in available_employees:
                    available_employees.remove(sick_request.rqst_date_employee)

        # Vacation requests (im going to be off this week or this day)
        if all_datetime_vacation:
            for vacation_request in all_datetime_vacation:
                if vacation_request.rqst_date_employee in available_employees:
                    available_employees.remove(vacation_request.rqst_date_employee)

        # ****************************************************************
        # *** add in duplicates in main list for emps with preferences ***

        # Vacation requests (im sick or am going to be sick (dr visit))
        if all_datetime_preferred:
            for request in all_datetime_preferred:
                if request.rqst_date_employee in available_employees:
                    available_employees.append(request.rqst_date_employee)
        if all_daytime_preferred:
            for request in all_daytime_preferred:
                if (
                    request.rqst_day_employee in available_employees
                    # if we've aready added them as a date time preference we dont 
                    # need to add them again if they normally prefer it..that would make 
                    # them 3x as likely to be picked for the shift
                    and available_employees.count(request.rqst_day_employee) < 2
                    ):
                    available_employees.append(request.rqst_day_employee)


        return_val = [None]*2

        # select random employee from final list and return it
        if available_employees:

            # init return val
            
            # get employee
            # TODO: Instead of getting the first get a random available employee
            # once we have stuff down well
            return_val[0] = available_employees[0]
            #return_val[0] = random.choice(available_employees)
            
            # get employee types for chosen employee
            chosen_employee_types = PersonEmployeeType.objects.filter(
                                                                        person_employee_type_user = self.user,
                                                                        pet_employee = return_val[0],
                                                                        )
            temp_chosen_employee_types = []
            for chosen_employee_type in chosen_employee_types:
                temp_chosen_employee_types.append(chosen_employee_type.pet_employee_type)

            # get list of chosen employee's types and what we need intersected
            chosen_employee_types_intersect = []
            chosen_employee_types_intersect = list(set.intersection(set(temp_chosen_employee_types),set(temp_emp_types_needed)))
            return_val[1] = chosen_employee_types_intersect[0]
            #return_val[1] = random.choice(chosen_employee_types_intersect)

        return return_val

    def HoursUntilCantWork(self,employee,datetime):
        '''
        ****************************************************
        Given Person Object, DateTime Date, DateTime Time

        return int of number of hours until the employee can't work
        given all the "can't work" requests specified (SICK,VACA,SKIP)

        ****************************************************
        ''' 

        date = self.date_model_obj.date
        time = datetime.time()

        # TODO: https://docs.djangoproject.com/en/1.8/ref/models/querysets/#django.db.models.query.QuerySet.latest
        # TODO: evaluate if 25 is the correct thing to do here or if it just happens to work 
        # TODO: there is a way to futher pair down the inital any list locally
        #       rather than hitting the server again look into

        # check to see if there are any requests
        qs_any_datetime_requests = RequestDateTime.objects.filter(
                                                                    request_date_time_user = self.user,
                                                                    rqst_date_employee = employee,
                                                                    rqst_date_date = date
                                                                    ).exclude(
                                                                                rqst_date_type = 'PREF')
        qs_any_daytime_requests = RequestDayTime.objects.filter(
                                                                request_day_time_user = self.user,
                                                                rqst_day_employee = employee,
                                                                day_of_week = date.weekday(),
                                                                rqst_day_type = 'SKIP')
        if( not(qs_any_datetime_requests)
            and not(qs_any_daytime_requests) ):
            return int(25 - time.hour)

        # check to see if the current time is currently in a request's time slot
        qs_during_datetime_requests = RequestDateTime.objects.filter(
                                                                        request_date_time_user = self.user,
                                                                        rqst_date_employee = employee,
                                                                        rqst_date_date = date,
                                                                        rqst_date_start_time__lte = time,
                                                                        rqst_date_end_time__gt = time
                                                                        ).exclude(
                                                                                    rqst_date_type = 'PREF')
        qs_during_daytime_requests = RequestDayTime.objects.filter(
                                                                    request_day_time_user = self.user,
                                                                    rqst_day_employee = employee,
                                                                    day_of_week = date.weekday(),
                                                                    rqst_day_start_time__lte = time,
                                                                    rqst_day_end_time__gt = time,
                                                                    rqst_day_type = 'SKIP')
        if qs_during_datetime_requests:
            return 0
        if qs_during_daytime_requests:
            return 0

        # check to see if there are any future requests
        qs_future_datetime_request = RequestDateTime.objects.filter(
                                                                    request_date_time_user = self.user,
                                                                    rqst_date_employee = employee,
                                                                    rqst_date_date = date,
                                                                    rqst_date_start_time__gte = time
                                                                    ).exclude(
                                                                                rqst_date__type = 'PREF'
                                                                                ).order_by(
                                                                                            "-rqst_date__start_time").first()
        qs_future_daytime_request = RequestDayTime.objects.filter(
                                                                    request_day_time_user = self.user,
                                                                    rqst_day_employee = employee,
                                                                    day_of_week = date.weekday(),
                                                                    rqst_day_start_time__gte = time,
                                                                    rqst_day__type = 'SKIP'
                                                                    ).order_by(
                                                                                "-rqst_day__start_time").first()
        if( qs_future_datetime_request ):
            return int(qs_future_datetime_request[0].rqst_date_start_time.hour - time.hour)
        if( qs_future_day_request ):
            return int(qs_future_day_request[0].rqst_day_start_time.hour - time.hour)

        return int(25 - time.hour)

    def ConvertTimeSliceToDateTime(self,time_slice):
        '''
            given a time slice determine the beginning time of the time slice
            that we are processing depending on the start of the day
        '''
        minutes_past_start = time_slice * self.TIMESLICE
        start_dt = dt.datetime(
                                    self.date_model_obj.date.year,
                                    self.date_model_obj.date.month,
                                    self.date_model_obj.date.day,
                                    self.date_model_obj.day_start_time.hour,
                                    self.date_model_obj.day_start_time.minute,
                                    self.date_model_obj.day_start_time.second,
                                    )
        time_slice_datetime = start_dt + datetime.timedelta(minutes = minutes_past_start)

        # TODO maybe need to round the datetime or nearest TIMESLICE
        return time_slice_datetime

    def RemoveActiveShifts(self,datetime):  
        '''
        ****************************************************
        Takes a list of shifts in active_shifts and updates it
        based on requirements and people working enough hours etc

        ****************************************************
        '''
        shifts_to_screen = self.shift_active
        # ------------------------------
        # remove active shifts based on hours worked
        # and hours available
        temp_active_shifts = []
        for active_shift in shifts_to_screen:

            # remove any shifts that have completed their max hour req for the day
            if( active_shift.hours() == active_shift.employee.person_max_hours_per_shift ):
                "prevent from active shift"
            # remove any shifts that the employee can't work the next hour
            # < 2 catches shift that should have ended already (0) and 
            # shift that is going to be over (1); (>=2) means they have at least another hour to work
            elif( self.HoursUntilCantWork(active_shift.employee,datetime) < 2 ):
                "prevent from active shift"
            else:
                temp_active_shifts.append(active_shift)
        
        # update active shifts list
        shifts_to_screen[:] = []
        shifts_to_screen = temp_active_shifts[:]
        temp_active_shifts[:] = []

        # -----------------------------------
        # remove active shifts based on having a higher number
        # of employees working than are required 
        # remove randomly for now maybe make smart enough to remove
        # workers who've worked more hours (that day or that week)

        # get dict of requirement types keyed by the type of employee (manager, cook, eye dr., etc)
        employee_type_requirements = {}
        employee_type_requirements = self.GetEmployeeTypeRequirements(datetime)

        if ( not(employee_type_requirements) ):
        
            # cancel all active shifts
            # maybe only cancel them when they have met a min shift requirment
            shifts_to_screen[:] = []
            
        else:
            # if we still have shifts then there is some work to be done still
            if( shifts_to_screen ):

                # for all the shifts, create a map of
                # { Employee_Type , [Shifts] }
                active_shifts_by_employee_type = {}
                for shift in shifts_to_screen:
                    if( shift.shift_employee_type.et_type in active_shifts_by_employee_type ):
                        active_shifts_by_employee_type[shift.shift_employee_type.et_type].append(shift)
                    else:
                        active_shifts_by_employee_type[shift.shift_employee_type.et_type] = [shift]
                    

                # for all the requirements get the first one and get its count so we have a mapt of
                # { Employee_Type , Count }
                requirement_count_by_employee_type = {}
                for employee_type, requirement_list in employee_type_requirements.items():
                    requirement_count_by_employee_type[employee_type] = requirement_list[0]


                # remove any shifts that dont have employee types not in employee requirements
                # and remove any shifts in employee types that have more worker than that are required.
                for employee_type, shift_list in active_shifts_by_employee_type.items():
                    if( employee_type in requirement_count_by_employee_type ):
                        if( requirement_count_by_employee_type[employee_type] > len(shift_list) ):
                            temp_active_shifts += shift_list
                        else:
                            temp_active_shifts += random.sample(shift_list,requirement_count_by_employee_type[employee_type])
        
                # update active shifts list
                shifts_to_screen[:] = []
                shifts_to_screen = temp_active_shifts[:]
                temp_active_shifts[:] = []
        return shifts_to_screen

