
def time_format(created_at):

    months = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day, time = created_at.split()
    hours, minutes, seconds = time.split(':')
    time = f"{hours}:{minutes}"
    year, month, day = day.split('-')
    month = months[int(month)-1]
    day = int(day)
    date_format = f"{time} {day} {month}"
    return date_format

