from urllib import request
from urllib.request import urlopen
import json
import datetime

APIID = '<INSERT API ID>'
APIKEY = '<INSERT API KEY>'
PAGEID = '56201213fea48b995a000c96'

days = {}
containers = {}
hours = {}
minutes = {}
durations = {}

# Multitenant, Sundays 12-14 Warsaw time
days.update({'AP02': 6})
containers.update({'AP02': '5ac3744f1e486604ebe5315a'})
hours.update({'AP02': 10})
minutes.update({'AP02': 00})
durations.update({'AP02': 2})

# Multitenant, Sundays 18-20 Warsaw time
days.update({'EU02': 6})
containers.update({'EU02': '56a9f4e7bca6d7835b0000d8'})
hours.update({'EU02': 16})
minutes.update({'EU02': 00})
durations.update({'EU02': 2})

# Customer X, Sundays 17:30-19:30 UAE time
days.update({'EU04': 6})
containers.update({'EU04': '5d245bb3a70c9b433e46cdd8'})
hours.update({'EU04': 13})
minutes.update({'EU04': 30})
durations.update({'EU04': 2})

# Multitenant Oracle, Sundays 17-20 Warsaw time
days.update({'EU07': 6})
containers.update({'EU07': '59bba53a98a4721be879939a'})
hours.update({'EU07': 15})
minutes.update({'EU07': 00})
durations.update({'EU07': 3})

# Customer Y, Sundays, 05-06 Chicago time
days.update({'US01': 6})
containers.update({'US01': '5620a00e6de34e1e5900015b'})
hours.update({'US01': 10})
minutes.update({'US01': 00})
durations.update({'US01': 1})

# Customer Z, Sundays, 12-14 Warsaw time
days.update({'US02': 6})
containers.update({'US02': '5620a017fd9cd31d59000bba'})
hours.update({'US02': 10})
minutes.update({'US02': 00})
durations.update({'US02': 2})

# customer Q, Sundays, 12-14 Warsaw time
days.update({'US03': 6})
containers.update({'US03': '5639cf6360d282da0e000932'})
hours.update({'US03': 10})
minutes.update({'US03': 00})
durations.update({'US03': 2})

# Multitenant, Sundays, 18-20 Warsaw time
days.update({'US04': 6})
containers.update({'US04': '5993f5f87db93888050004f2'})
hours.update({'US04': 16})
minutes.update({'US04': 00})
durations.update({'US04': 2})

headers = {
    'Content-Type': 'application/json',
    'x-api-id': APIID,
    'x-api-key': APIKEY
}


def get_maintenances():

    status_request = request.Request('https://api.status.io/v2/maintenances/' + PAGEID, headers=headers)

    response_body = urlopen(status_request).read()

    print(response_body)

    data = json.loads(response_body.decode('utf-8'))

    maintenances = []

    if data['status']['message'] != 'OK':
        quit()

    for maintenance in data['result']['upcoming_maintenances']:
        maintenances.append(maintenance)

    return maintenances


def get_maintenance_details(mw_id):
    status_request = request.Request('https://api.status.io/v2/maintenance/' + PAGEID + '/' + mw_id, headers=headers)

    response_body = urlopen(status_request).read()

    data = json.loads(response_body.decode('utf-8'))
    return data['result']['containers_affected'][0]['_id']


def create_maintenance(code):
    days_to_next = 1

    while (datetime.datetime.today()+datetime.timedelta(days=days_to_next)).weekday() != days[code]:
        days_to_next += 1

    values = """
      {
        "statuspage_id": \"""" + PAGEID + """",
        "components": [
          "5620127dfea48b995a000ca9",
          "56334873421970db0e0002d3",
          "56201213fea48b995a000ca6",
          "568506cc01cb23db4900006d"
        ],
        "containers": [
          \""""+containers[code]+""""
        ],
        "all_infrastructure_affected": "0",
        "automation": "1",
        "maintenance_name": \""""+code+""" Weekly production maintenance window",
        "maintenance_details": "Standard weekly production maintenance window.",
        "date_planned_start": \""""+(datetime.datetime.today()
                                     + datetime.timedelta(days=days_to_next)).strftime('%m/%d/%Y')+"""",
        "time_planned_start": \""""+str(hours[code])+""":"""+str(minutes[code])+"""",
        "date_planned_end": \""""+(datetime.datetime.today()
                                   + datetime.timedelta(days=days_to_next)).strftime('%m/%d/%Y')+"""",
        "time_planned_end": \""""+str(hours[code]+durations[code])+""":"""+str(minutes[code])+"""",
        "maintenance_notify_now": "1",
        "maintenance_notify_72_hr": "0",
        "maintenance_notify_24_hr": "0",
        "maintenance_notify_1_hr": "0"
      }
    """

    parsed_values = values.encode("utf-8")
    status_request = request.Request('https://api.status.io/v2/maintenance/schedule', data=parsed_values,
                                     headers=headers)

    response_body = urlopen(status_request).read()
    scheduling_status = json.loads(response_body.decode('utf-8'))
    if scheduling_status['status']['error'] == "no":
        print("Maintenance for %s has been successfully scheduled" % code)
    else:
        print("There were some errors while scheduling maintenance for %s" % code)
        print(response_body)


def remove_maintenance(mw_id):
    values = """
      {
        "statuspage_id": \"""" + PAGEID + """",
        "maintenance_id": \""""+mw_id+""""
      }
    """

    parsed_values = values.encode("utf-8")
    status_request = request.Request('https://api.status.io/v2/maintenance/delete', data=parsed_values, headers=headers)
    response_body = urlopen(status_request).read()
    print(response_body)


if __name__ == '__main__':

    scheduled_maintenances = []

    for maintenance_id in get_maintenances():
        # remove_maintenance(maintenance_id)
        scheduled_maintenances.append(get_maintenance_details(maintenance_id))

    print(scheduled_maintenances)

    for key, value in containers.items():
        if value not in scheduled_maintenances:
            print('I will schedule ' + key)
            create_maintenance(key)
        else:
            print('I will not schedule ' + key)
