## Configuration options

| Key | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `name` | `string` | `False` | `Rozkładzik` | Name of sensor |
| `city` | `string` | `True` | - | Name of city used in API |
| `stops` | `list` | `True` | - | List of stops to monitor |

### Configuration for stop

| Key | Description |
| --- | --- | 
| `id` | ID of stop |
| `name` | Name of stop |
| `stops_group_mode` | Enables stops group mode. Possible values: `true`, `false`. |
| `lines` | `list` | `False` | all available | List of monitored lines. |
| `directions` | `list` | `False` | all available | List of monitored directions. |

## Example usage

```
sensor:
  - platform: rozkladzik
    city: 'wroclaw'
    stops:
      - id: 1281
        name: 'Plac Grunwaldzki'
        directions:
          - "Reja"
      - id: 94
        name: 'Rynek'
        stops_group_mode: true
        lines:
          - "33"
```

## Hints

* This sensor provides attributes which can be used in [*HTML card*](https://github.com/PiotrMachowski/Home-Assistant-Lovelace-HTML-card) or [*HTML Template card*](https://github.com/PiotrMachowski/Home-Assistant-Lovelace-HTML-Template-card): `html_timetable`, `html_departures`
  * HTML Card:
    ```yaml
    - type: custom:html-card
      title: 'Rozkładzik'
      content: |
        <big><center>Departures</center></big>
        [[ sensor.rozkladzik_wroclaw_1709.attributes.html_departures ]]
        <big><center>Timetable</center></big>
        [[ sensor.rozkladzik_wroclaw_1709.attributes.html_timetable ]]
    ```
  * HTML Template Card:
    ```yaml
    - type: custom:html-template-card
      title: 'Rozkładzik'
      ignore_line_breaks: true
      content: |
        <big><center>Departures</center></big>
        {{ state_attr('sensor.rozkladzik_wroclaw_1709','html_departures') }}
        <big><center>Timetable</center></big>
        {{ state_attr('sensor.rozkladzik_wroclaw_1709','html_timetable') }}
    ```

## FAQ

* **How to get values for configuration parameters?**

  To find out values for configuration parameters follow the following steps: 
  - Go to [rozkladzik.pl](https://www.rozkladzik.pl) and find desired stop.
  - Activate developer tools using `[F12]` button.
  - Click on chosen stop and in network tab look for call to `https://www.rozkladzik.pl/<name_of_city>/timetable.txt?...` URL
  - Value for `stops_group_mode` is determined by value of query parameter `c`. If it is equal to `bsa` you have to enable group mode.
  - Value for `city` comes from `<name_of_city>` path fragment.
  - Value for `id` comes from query parameter `t` or `b` for group mode.
