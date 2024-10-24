import json
import logging
import pytz
from datetime import datetime, timedelta, time
from icalendar import Calendar, Event

def read_json_file(filename):
    encodings = ['utf-8-sig', 'gbk', 'utf-8']
    for enc in encodings:
        try:
            with open(filename, 'r', encoding=enc) as f:
                data = f.read()
                # Try to parse JSON
                json_data = json.loads(data)
                logging.info(f"Successfully read and parsed {filename} with encoding {enc}")
                return json_data
        except UnicodeDecodeError as e:
            logging.warning(f"Failed to read {filename} with encoding {enc}: {e}")
        except json.JSONDecodeError as e:
            logging.warning(f"Failed to parse JSON in {filename} with encoding {enc}: {e}")
    raise Exception(f"Failed to read and parse {filename} with known encodings.")

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

    settings_filename = 'settings.json'
    try:
        settings = read_json_file(settings_filename)
    except Exception as e:
        logging.error(f"Error reading {settings_filename}: {e}")
        return

    # Get SelectedProfile from settings
    selected_profile = settings.get('SelectedProfile', 'main.json')
    logging.info(f"Selected profile: {selected_profile}")

    # Read main.json (or the selected profile)
    try:
        data = read_json_file(selected_profile)
    except Exception as e:
        logging.error(f"Error reading {selected_profile}: {e}")
        return

    # Extract SingleWeekStartTime
    single_week_start_time_str = settings.get('SingleWeekStartTime', '2024-09-01T00:00:00')
    try:
        single_week_start_time = datetime.fromisoformat(single_week_start_time_str)
    except ValueError as e:
        logging.error(f"Invalid SingleWeekStartTime format in {settings_filename}: {e}")
        return
    logging.info(f"SingleWeekStartTime: {single_week_start_time}")

    # Extract ClassPrepareNotifySeconds (not used in this script but logged)
    class_prepare_notify_seconds = settings.get('ClassPrepareNotifySeconds', 60)
    logging.info(f"ClassPrepareNotifySeconds: {class_prepare_notify_seconds}")

    # Extract subjects
    subjects = data.get('Subjects', {})
    subjects_dict = {}
    for subject_id, subject_info in subjects.items():
        name = subject_info.get('Name', '')
        initial = subject_info.get('Initial', '')
        teacher_name = subject_info.get('TeacherName', '')
        subjects_dict[subject_id] = {
            'name': name,
            'initial': initial,
            'teacher_name': teacher_name,
        }

    # Extract time layouts
    time_layouts = data.get('TimeLayouts', {})
    time_layouts_dict = {}
    for layout_id, layout_info in time_layouts.items():
        name = layout_info.get('Name', '')
        layouts = layout_info.get('Layouts', [])
        time_layouts_dict[layout_id] = {
            'name': name,
            'layouts': layouts,  # List of time slots
        }

    # Extract class plans
    class_plans = data.get('ClassPlans', {})
    class_plans_list = []
    for plan_id, plan_info in class_plans.items():
        time_layout_id = plan_info.get('TimeLayoutId', '')
        time_rule = plan_info.get('TimeRule', {})
        classes = plan_info.get('Classes', [])
        name = plan_info.get('Name', '')
        is_enabled = plan_info.get('IsEnabled', False)
        class_plans_list.append({
            'id': plan_id,
            'TimeLayoutId': time_layout_id,
            'TimeRule': time_rule,
            'Classes': classes,
            'Name': name,
            'IsEnabled': is_enabled,
        })

    # Set up calendar
    cal = Calendar()
    cal.add('prodid', '-//ClassIsland Schedule//')
    cal.add('version', '2.0')
    tz = pytz.timezone('Asia/Shanghai')

    # Define start and end dates
    start_date = single_week_start_time.date()
    end_date = datetime(2025, 6, 30).date()  # Adjusted to match China's academic calendar
    logging.info(f"Calendar will cover from {start_date} to {end_date}")

    # Map data weekdays to RRULE BYDAY values
    weekday_map = {
        0: 'MO',
        1: 'TU',
        2: 'WE',
        3: 'TH',
        4: 'FR',
        5: 'SA',
        6: 'SU',
    }

    # Define timespan to ignore (7:00 PM to 10:30 PM)
    ignore_start_time = time(19, 0)  # 7:00 PM
    ignore_end_time = time(22, 30)   # 10:30 PM

    # Define the specific class name to ignore
    ignore_class_names = ['眼保健操', '课间操', '晚训']

    for plan in class_plans_list:
        if not plan.get('IsEnabled'):
            logging.info(f"Skipping disabled ClassPlan '{plan['Name']}'")
            continue
        time_rule = plan.get('TimeRule', {})
        data_weekday = time_rule.get('WeekDay')
        if data_weekday is None:
            logging.warning(f"No WeekDay in TimeRule for ClassPlan '{plan['Name']}'")
            continue
        # Map data_weekday to Python weekday (Monday=0)
        python_weekday = (data_weekday - 1) % 7
        time_layout_id = plan.get('TimeLayoutId')
        time_layout = time_layouts_dict.get(time_layout_id)
        if time_layout is None:
            logging.warning(f"No TimeLayout with ID '{time_layout_id}' for ClassPlan '{plan['Name']}'")
            continue
        all_time_slots = time_layout.get('layouts', [])
        # Filter time slots to include only class periods (TimeType == 0)
        class_time_slots = [slot for slot in all_time_slots if slot.get('TimeType') == 0]
        classes = plan.get('Classes', [])
        if len(classes) != len(class_time_slots):
            logging.warning(f"Number of classes {len(classes)} does not match number of class periods {len(class_time_slots)} in ClassPlan '{plan['Name']}'")
            # Proceed and match as many classes and time slots as possible

        # Find the first occurrence date for this plan
        first_occurrence_date = start_date
        days_ahead = (python_weekday - first_occurrence_date.weekday()) % 7
        first_occurrence_date += timedelta(days=days_ahead)

        for idx, cls in enumerate(classes):
            if idx >= len(class_time_slots):
                logging.warning(f"More classes than time slots in ClassPlan '{plan['Name']}' at index {idx}")
                break  # No more time slots available
            subject_id = cls.get('SubjectId')
            if not subject_id:
                logging.info(f"Skipping empty class at index {idx} in ClassPlan '{plan['Name']}'")
                continue  # Skip if no subject
            subject = subjects_dict.get(subject_id)
            if not subject:
                logging.warning(f"No subject with ID '{subject_id}'")
                continue
            subject_name = subject.get('name')
            teacher_name = subject.get('teacher_name')

            # Skip the specific class to ignore
            if subject_name in ignore_class_names:
                logging.info(f"Skipping class '{subject_name}' as it is set to be ignored")
                continue

            # Get the time slot
            time_slot = class_time_slots[idx]
            start_second = time_slot.get('StartSecond')
            end_second = time_slot.get('EndSecond')
            if start_second is None or end_second is None:
                logging.warning(f"No start or end time in time slot index {idx} for ClassPlan '{plan['Name']}'")
                continue
            # Convert 'StartSecond' and 'EndSecond' from ISO format strings to datetime.time objects
            try:
                start_dt = datetime.fromisoformat(start_second)
                end_dt = datetime.fromisoformat(end_second)
                # Extract time with timezone info
                start_time = start_dt.timetz()
                end_time = end_dt.timetz()
            except Exception as e:
                logging.warning(f"Error parsing time in time slot index {idx} for ClassPlan '{plan['Name']}': {e}")
                continue

            # Skip events within the ignore timespan
            start_time_naive = start_time.replace(tzinfo=None)
            if ignore_start_time <= start_time_naive <= ignore_end_time:
                logging.info(f"Skipping class '{subject_name}' starting at {start_time} as it falls within the ignore timespan")
                continue

            # Create the event
            event = Event()
            event.add('summary', subject_name)
            if teacher_name:
                event.add('location', teacher_name)

            # Create datetime objects for event start and end
            dtstart = datetime.combine(first_occurrence_date, start_time)
            dtend = datetime.combine(first_occurrence_date, end_time)
            # Ensure dtstart and dtend are timezone-aware
            if dtstart.tzinfo is None:
                dtstart = tz.localize(dtstart)
            if dtend.tzinfo is None:
                dtend = tz.localize(dtend)

            # Add dtstart and dtend with correct TZID
            event.add('dtstart', dtstart)
            event['dtstart'].params['TZID'] = 'Asia/Shanghai'

            event.add('dtend', dtend)
            event['dtend'].params['TZID'] = 'Asia/Shanghai'

            # Compute UNTIL in UTC and format it correctly
            until_dt = datetime.combine(end_date, time(23, 59, 59))
            until_dt_utc = tz.localize(until_dt).astimezone(pytz.utc)

            # Build RRULE as a dictionary
            rrule_dict = {
                'freq': 'weekly',
                'until': until_dt_utc,
                'byday': [weekday_map.get(python_weekday)],
                'wkst': 'MO',
            }
            event.add('rrule', rrule_dict)

            cal.add_component(event)
            logging.info(f"Added event: '{subject_name}' starting on {first_occurrence_date} at {start_time} - {end_time}")

    # Write calendar to file
    output_filename = 'schedule.ics'
    try:
        with open(output_filename, 'wb') as f:
            f.write(cal.to_ical())
        logging.info(f"Successfully wrote calendar to '{output_filename}'")
    except Exception as e:
        logging.error(f"Error writing to '{output_filename}': {e}")

if __name__ == '__main__':
    main()
