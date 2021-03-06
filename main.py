import numpy as np
from collections import defaultdict
from csvProcessor import CsvProcessor
from showDAP import showHistogram

file_enrollment = "data/enrollments.csv"
file_daily_engagement = "data/daily_engagement.csv"
file_project_submissions = "data/project_submissions.csv"

csv = CsvProcessor()
enrollments = csv.read(file_enrollment)
daily_engagement = csv.read(file_daily_engagement)
project_submissions = csv.read(file_project_submissions)

# Clean up the data types in enrollment
attris = { 'join_date', 'cancel_date', 'days_to_cancel', 'is_udacity', 'is_canceled' }
csv.data_type_process(enrollments, attris)

attris = { 'utc_date', 'total_minutes_visited', 'lessons_completed', 'num_courses_visited' }
csv.data_type_process(daily_engagement, attris)

# For each of these three tables, find the number of rows in the table and
# the number of unique students in the table. To find the number of unique
# students, you might want to create a set of the account keys in each table.
def get_unique_values(elements, key):
    elements_set = set()
    for e in elements:
        value = e[key]
        elements_set.add(value)
    return elements_set

unique_enrollments = get_unique_values(enrollments, "account_key")
print(len(enrollments))
print(len(unique_enrollments))

unique_daily_engagement = get_unique_values(daily_engagement, "account_key")
print(len(daily_engagement))
print(len(unique_daily_engagement))

unique_project_submissions = get_unique_values(project_submissions, "account_key")
print(len(project_submissions))
print(len(unique_project_submissions))

# Why are students missing from daily_engagement?
print("Why are students missing from daily_engagement?")
for enrollment in enrollments:
    student = enrollment['account_key']
    if student not in unique_daily_engagement \
        and enrollment['days_to_cancel'] != 0: # join_date = cancel_date
            print(enrollment)

# Remove udacity test accouts
udacity_test_accounts = set()
for enrollment in enrollments:
    if enrollment['is_udacity']:
        udacity_test_accounts.add(enrollment['account_key'])
print("Udacity accounts: " + str(len(udacity_test_accounts)))

def remove_udacity_account(data):
    non_udacity_data = []
    for d in data:
        if d['account_key'] not in udacity_test_accounts:
            non_udacity_data.append(d)
    return non_udacity_data

non_udacity_enrollments = remove_udacity_account(enrollments)
print(len(non_udacity_enrollments))

non_udacity_daily_engagement = remove_udacity_account(daily_engagement)
print(len(non_udacity_daily_engagement))

non_udacity_project_submissions = remove_udacity_account(project_submissions)
print(len(non_udacity_project_submissions))

surprising_data_points = []
for enrollment in non_udacity_enrollments:
    student = enrollment['account_key']
    if student not in unique_daily_engagement \
        and enrollment['days_to_cancel'] != 0:
            surprising_data_points.append(enrollment)
if len(surprising_data_points):
    print(surprising_data_points)
else:
    print("No special data points.")

# Create a dictionary of students who either:
# haven't cancel yet
# stayed enrolled more than 7 days
paid_student = {}
for enrollment in non_udacity_enrollments:
    if not enrollment['is_canceled'] or enrollment['days_to_cancel'] > 7:
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']
        # Keep the most recent join date
        if account_key not in paid_student \
            or enrollment_date > paid_student[account_key]:
            paid_student.update({enrollment['account_key']: enrollment['join_date']})
print("Paid student: " + str(len(paid_student)))

# Remove free-trial and cancels
def remove_free_trial_cancels(data):
    paid_data = []
    for d in data:
        if d['account_key'] in paid_student:
            paid_data.append(d)
    return paid_data

# Create a list of engagement records containing only data
# for paid students during their fist week
def within_one_week(start_date, end_date):
    duration = end_date - start_date
    return duration.days < 7 and duration.days >= 0

paid_engagements = remove_free_trial_cancels(daily_engagement)
paid_engagements_first_week = []
for submission in paid_engagements:
    student_id = submission['account_key']
    is_valid = within_one_week(paid_student[student_id], submission['utc_date'])
    if is_valid:
        paid_engagements_first_week.append(submission)
print(len(paid_engagements_first_week))

# Average minutes spent in classroom
def get_group_data(data, key):
    ret_data = defaultdict(list)
    for engagement in data:
        ret_data[engagement[key]].append(engagement)
    return ret_data

def get_sum(grouped_data, key):
    account_minutes_dict = {}
    for account_key, engagements in grouped_data.items():
        total_minutes = 0;
        for engagement in engagements:
            total_minutes += engagement[key]
        account_minutes_dict[account_key] = total_minutes
    return account_minutes_dict

paid_engagements_dict = get_group_data(paid_engagements_first_week, 'account_key')
account_minutes_dict = get_sum(paid_engagements_dict, 'total_minutes_visited')

total_minutes_list = list(account_minutes_dict.values())
avg_minutes = np.average(total_minutes_list)
print(avg_minutes)

mean_minutes = np.average(total_minutes_list)
print(mean_minutes)

sd_minutes = np.std(total_minutes_list)
print(sd_minutes)

min_minutes = np.min(total_minutes_list)
print(min_minutes)

max_minutes = np.max(total_minutes_list)
print(max_minutes)

# Debugging Data Problems
def get_key(dict, expected_val):
    for key, value in dict.items():
        if value == expected_val:
            return key
    return None

max_minutes_account = get_key(account_minutes_dict, max_minutes)
max_minutes_engagements = paid_engagements_dict[max_minutes_account]
for submission in max_minutes_engagements:
    print(submission)


def data_description(data, note):
    print(note)
    print("Mean: " + str(np.average(data)))
    print("SD: " + str(np.std(data)))
    print("Min: " + str(np.min(data)))
    print("Max: " + str(np.max(data)))
    showHistogram(data, note)

paid_engagements_dict = get_group_data(paid_engagements_first_week, 'account_key')

# Average completed lessons in classroom
account_completed_lessons_dict = get_sum(paid_engagements_dict, 'lessons_completed')
data_description(list(account_completed_lessons_dict.values()), "Completed lessons")

# Analyzing 'num_courses_visited'
for account_key, engagements in paid_engagements_dict.items():
    for submission in engagements:
        submission['has_visited'] = int(bool(submission['num_courses_visited']))

account_visited_days_dict = get_sum(paid_engagements_dict, 'has_visited')
data_description(list(account_visited_days_dict.values()), "Visited days")

# Spliting out passing students of 'subway project'
paied_submissions = remove_free_trial_cancels(project_submissions)

subway_project_keys = ['746169184', '3176718735']
pass_subway_project_account = set()
for submission in paied_submissions:
    project = submission['lesson_key']
    rating = submission['assigned_rating']
    if project in subway_project_keys \
        and (rating == 'PASSED' or rating == 'DISTINCTION'):
            pass_subway_project_account.add(submission['account_key'])

pass_engagements = []
nonpass_engagements = []
for engagement in paid_engagements_first_week:
    if engagement['account_key'] in pass_subway_project_account:
        pass_engagements.append(engagement)
    else:
        nonpass_engagements.append(engagement)

print("Passed/Non-passed: " + str(len(pass_engagements)) + "/" + str(len(nonpass_engagements)))

# Comparing the 2 group of students(passed, non-passed)
def get_account_attrisum_list(data, attri):
    account_pass_engagement_dict = get_group_data(data, 'account_key')
    account_minutes_dict = get_sum(account_pass_engagement_dict, attri)
    return list(account_minutes_dict.values())

pass_minutes_list = get_account_attrisum_list(pass_engagements,'total_minutes_visited')
data_description(pass_minutes_list, "Pass on total minutes")
nonpass_minutes_list = get_account_attrisum_list(nonpass_engagements, 'total_minutes_visited');
data_description(nonpass_minutes_list, "Non-pass on total minutes")

pass_completed_lessons_list = get_account_attrisum_list(pass_engagements,'lessons_completed')
data_description(pass_completed_lessons_list, "Pass on completed lessons")
nonpass_completed_lessons_list = get_account_attrisum_list(nonpass_engagements, 'lessons_completed');
data_description(nonpass_completed_lessons_list, "Non-pass on completed lessons")

pass_visited_days_list = get_account_attrisum_list(pass_engagements,'has_visited')
data_description(pass_visited_days_list, "Pass on visited days")
nonpass_visited_days_list = get_account_attrisum_list(nonpass_engagements, 'has_visited');
data_description(nonpass_visited_days_list, "Non-pass on visited days")

