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
CONF_CITY = 'city'

DEFAULT_NAME = 'Rozkładzik'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_CITY): cv.string,
    vol.Required(CONF_STOPS): vol.All(cv.ensure_list, [
        vol.Schema({
            vol.Required(CONF_STOP_ID): cv.positive_int,
            vol.Required(CONF_STOP_NAME): cv.string,
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
        uid = '{}_{}_{}'.format(name, city, stop_id)
        entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)
        dev.append(RozkladzikSensor(entity_id, name, city, stop_id, stop_name))
    add_entities(dev, True)


class RozkladzikSensor(Entity):
    def __init__(self, entity_id, name, city, stop_id, stop_name):
        self.entity_id = entity_id
        self._name = name
        self._stop_id = stop_id
        self._stop_name = stop_name
        self._city = city
        self._departures_number = None
        self._departures_ordered = []
        self._departures_by_line = dict()
        self._state = None

    @property
    def name(self):
        return '{} {} - {}'.format(self._name, self._city, self._stop_name)

    @property
    def state(self):
        if self._departures_number is not None and self._departures_number > 0:
            dep = self._departures_ordered[0]
            return '{}: {} ({}m)'.format(dep[0], dep[1], dep[2])
        return None

    @property
    def unit_of_measurement(self):
        return None

    @property
    def device_state_attributes(self):
        attr = dict()
        if self._departures_ordered is not None:
            attr['list'] = self._departures_ordered
            attr['html'] = self.get_html()
        return attr

    def update(self):
        now = datetime.datetime.now()
        r_time = now.hour * 60 + now.minute
        url_template = 'https://www.rozkladzik.pl/{}/timetable.txt?c=tsa&t={}&day={}&time={}'
        response = requests.get(url_template.format(self._city, self._stop_id, now.weekday(), r_time))
        if response.status_code == 200 and response.content.__len__() > 0:
            raw_array = response.text.split("|")
            self._departures_ordered = []
            self._departures_by_line = dict()
            for r in raw_array:
                line, departures = self.process_raw(r, r_time)
                self._departures_by_line[line] = []
                for departure_time, departure_diff in departures:
                    self._departures_ordered.append((line, departure_time, departure_diff))
                    self._departures_by_line[line].append((departure_time, departure_diff))
                self._departures_by_line[line].sort(key=lambda e: e[1])
            self._departures_ordered.sort(key=lambda e: e[2])
            self._departures_number = len(self._departures_ordered)

    def get_html(self):
        html = '<table width="100%" border=1 style="border: 1px black solid; border-collapse: collapse;">\n'
        lines = list(self._departures_by_line.keys())
        lines.sort()
        for line in lines:
            if len(self._departures_by_line[line]) == 0:
                continue
            html = html + '<tr><td style="text-align: center; padding: 4px"><big>{}</big></td>'.format(line)
            departures = ', '.join(map(lambda x: x[0], self._departures_by_line[line]))
            html = html + '<td style="text-align: right; padding: 4px">{}</td></tr>\n'.format(departures)
        if len(lines) == 0:
            html = html + '<tr><td style="text-align: center; padding: 4px">Brak połączeń</td>'
        html = html + '</table>'
        return html

    @staticmethod
    def process_raw(raw, now):
        raw = raw[:raw.find("#")]
        raw_split = raw.split(";")
        line = raw_split[0]
        times = []
        for i in range(3, len(raw_split), 4):
            time = int(raw_split[i])
            diff = time - now
            if diff < 0:
                diff += 1440
            hour = time // 60
            minute = time % 60
            t = "{:02}:{:02}".format(hour, minute)
            times.append((t, diff))
        return line, times
