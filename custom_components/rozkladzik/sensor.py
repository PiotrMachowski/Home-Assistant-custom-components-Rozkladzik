import requests
import datetime

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, ENTITY_ID_FORMAT
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity import async_generate_entity_id

CONF_STOPS = 'stops'
CONF_STOP_ID = 'id'
CONF_STOP_NAME = 'name'
CONF_GROUP_MODE = 'stops_group_mode'
CONF_LINES = 'lines'
CONF_DIRECTIONS = 'directions'
CONF_CITY = 'city'

DEFAULT_NAME = 'Rozkładzik'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_CITY): cv.string,
    vol.Required(CONF_STOPS): vol.All(cv.ensure_list, [
        vol.Schema({
            vol.Required(CONF_STOP_ID): cv.positive_int,
            vol.Required(CONF_STOP_NAME): cv.string,
            vol.Optional(CONF_GROUP_MODE, default=False): cv.boolean,
            vol.Optional(CONF_LINES, default=[]): cv.ensure_list,
            vol.Optional(CONF_DIRECTIONS, default=[]): cv.ensure_list
        })])
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    city = config.get(CONF_CITY)
    stops = config.get(CONF_STOPS)
    dev = []
    for stop in stops:
        stop_id = stop.get(CONF_STOP_ID)
        stop_name = stop.get(CONF_STOP_NAME)
        group_mode = stop.get(CONF_GROUP_MODE)
        lines = stop.get(CONF_LINES)
        directions = stop.get(CONF_DIRECTIONS)
        uid = '{}_{}_{}'.format(name, city, stop_id)
        entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)
        dev.append(RozkladzikSensor(entity_id, name, city, stop_id, stop_name, group_mode, lines, directions))
    add_entities(dev, True)


class RozkladzikSensor(Entity):
    def __init__(self, entity_id, name, city, stop_id, stop_name, group_mode, watched_lines, watched_directions):
        self.entity_id = entity_id
        self._name = name
        self._stop_id = stop_id
        self._stop_name = stop_name
        self._city = city
        self._city_data = self.get_city_data()
        self._group_mode = group_mode
        self._watched_lines = watched_lines
        self._watched_directions = watched_directions
        self._last_response = None
        self._departures_number = 0
        self._departures_ordered = []
        self._departures_by_line = dict()
        self._state = None

    @property
    def name(self):
        return '{} {} - {}'.format(self._name, self._city, self._stop_name)

    @property
    def state(self):
        if self._departures_number is not None and self._departures_number > 0:
            return RozkladzikSensor.departure_to_str(self._departures_ordered[0])
        return None

    @staticmethod
    def departure_to_str(departure):
        return '{} kier. {}: {} ({}m)'.format(departure[0], departure[1], departure[2], departure[3])

    @property
    def unit_of_measurement(self):
        return None

    @property
    def extra_state_attributes(self):
        attr = dict()
        if self._departures_ordered is not None:
            attr['list'] = self._departures_ordered
            attr['html_timetable'] = self.get_html_timetable()
            attr['html'] = attr['html_timetable']
            attr['html_departures'] = self.get_html_departures()
            if self._departures_number > 0:
                dep = self._departures_ordered[0]
                attr['line'] = dep[0]
                attr['direction'] = dep[1]
                attr['departure'] = dep[2]
                attr['time_to_departure'] = dep[3]
        return attr

    def update(self):
        now = datetime.datetime.now()
        r_time = now.hour * 60 + now.minute
        if self._should_update(r_time):
            url_template = 'https://www.rozkladzik.pl/{}/timetable.txt?c=tsa&t={}&day={}&time={}'
            if self._group_mode:
                url_template = 'https://www.rozkladzik.pl/{}/timetable.txt?c=bsa&b={}&day={}&time={}'
            response = requests.get(url_template.format(self._city, self._stop_id, now.weekday(), r_time))
            if response.status_code == 200 and response.content.__len__() > 0:
                self._last_response = response.text
        if self._last_response is not None:
            self.update_values_for_time(r_time)

    def _should_update(self, now):
        return self._last_response is None or self._departures_ordered is None or len(self._departures_ordered) == 0 or self._departures_ordered[0][4] < now

    def update_values_for_time(self, r_time):
        raw_array = self._last_response.split("|")
        self._departures_ordered = []
        self._departures_by_line = dict()
        departures_by_line = dict()
        lines_directions = dict()
        for r in raw_array:
            line, direction_number, departures = self.process_raw(r, r_time)
            direction = self.get_direction(line, direction_number)
            if len(self._watched_lines) > 0 and line not in self._watched_lines \
                    or len(self._watched_directions) > 0 and direction not in self._watched_directions:
                continue
            if not line in lines_directions:
                lines_directions[line] = []
            lines_directions[line].append(direction)
            departures_by_line[(line, direction)] = []
            for departure_time, departure_diff, departure_timestamp in departures:
                self._departures_ordered.append((line, direction, departure_time, departure_diff, departure_timestamp))
                departures_by_line[(line, direction)].append((departure_time, departure_diff))
            departures_by_line[(line, direction)].sort(key=lambda e: e[1])
        for line in lines_directions:
            self._departures_by_line[line] = dict()
            for direction in lines_directions[line]:
                self._departures_by_line[line][direction] = []
                for departure in departures_by_line[(line, direction)]:
                    self._departures_by_line[line][direction].append(departure)
        self._departures_ordered.sort(key=lambda e: e[3])
        self._departures_number = len(self._departures_ordered)

    def get_html_timetable(self):
        html = '<table width="100%" border=1 style="border: 1px black solid; border-collapse: collapse;">\n'
        lines = list(self._departures_by_line.keys())
        lines.sort()
        for line in lines:
            directions = list(self._departures_by_line[line].keys())
            directions.sort()
            for direction in directions:
                if len(direction) == 0:
                    continue
                html = html + '<tr><td style="text-align: center; padding: 4px"><big>{}, kier. {}</big></td>'.format(line, direction)
                departures = ', '.join(map(lambda x: x[0], self._departures_by_line[line][direction]))
                html = html + '<td style="text-align: right; padding: 4px">{}</td></tr>\n'.format(departures)
        if len(lines) == 0:
            html = html + '<tr><td style="text-align: center; padding: 4px">Brak połączeń</td>'
        html = html + '</table>'
        return html

    def get_html_departures(self):
        html = '<table width="100%" border=1 style="border: 1px black solid; border-collapse: collapse;">\n'
        for departure in self._departures_ordered:
            html = html + '<tr><td style="text-align: center; padding: 4px">{}</td></tr>\n'.format(
                RozkladzikSensor.departure_to_str(departure))
        html = html + '</table>'
        return html

    def get_city_data(self):
        url_template = 'https://www.rozkladzik.pl/{}/data.txt'
        response = requests.get(url_template.format(self._city))
        data = response.text
        lines = data.split("#SEP#")
        stopNames = lines[0].split(";")
        linesData = lines[11].split("#!#")
        lineDefinitions = dict()
        for lineData in linesData:
            rows = lineData.split(";")
            lineName = rows[0]
            lineDirections = []
            for i in range(0, len(rows) - 2, 5):
                directionId = int(rows[i + 2])
                directionName = stopNames[directionId]
                stops = rows[i + 3].split("|")
                lineDirection = (directionId, directionName, stops)
                lineDirections.append(lineDirection)
            lineDefinition = (lineName, lineDirections)
            lineDefinitions[lineName] = lineDefinition
        return lineDefinitions

    def get_direction(self, line, direction_number):
        return self._city_data[line][1][direction_number][1]

    @staticmethod
    def process_raw(raw, now):
        raw = raw[:raw.find("#")]
        raw_split = raw.split(";")
        line = raw_split[0]
        direction_number = int(raw_split[1])
        times = []
        for i in range(3, len(raw_split), 4):
            time = int(raw_split[i])
            diff = time - now
            if diff < 0:
                diff += 1440
            hour = time // 60
            minute = time % 60
            t = "{:02}:{:02}".format(hour, minute)
            times.append((t, diff, time))
        return line, direction_number, times
