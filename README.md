# Rozkładzik sensor

This sensor uses unofficial API to get data from [*Rozkładzik.pl*](https://www.rozkladzik.pl) and provide information about departures for chosen stop.

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

## Example usage

```
sensor:
  - platform: rozkladzik
    city: 'wroclaw'
    stops:
      - id: 1281
        name: 'Plac Grunwaldzki'
      - id: 1709
        name: 'Rynek'
```

## Instalation

Download [*sensor.py*](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/raw/master/sensor.py) and [*manifest.json*](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/raw/master/manifest.json) to `config/custom_compoments/rozkladzik` directory:
```bash
mkdir -p custom_compoments/rozkladzik
cd custom_compoments/rozkladzik
wget https://github.com/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/raw/master/sensor.py
wget https://github.com/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/raw/master/manifest.json
```


## Hints

This sensor provide `html` attribute which can be used in [*Lovelace HTML card*](https://github.com/PiotrMachowski/Home-Assistant-Lovelace-HTML-card):
```yaml
- type: custom:html-card
  title: 'Rozkładzik'
  data:
    - html: '<big><center>Departures</center></big>'
    - entity_id: sensor.rozkladzik_wroclaw_1709
      attribute: html
```

## FAQ

* **How to get values for configuration parameters?**

  To find out values for configuration parameters follow the following steps: 
  - Go to [rozkladzik.pl](https://www.rozkladzik.pl) and find desired stop.
  - Activate developer tools using `[F12]` button.
  - Click on chosen stop and in network tab look for call to `https://www.rozkladzik.pl/<name_of_city>/timetable.txt?...` URL
  - Value for `city` comes from `<name_of_city>` path fragment.
  - Value for `id` comes from query string parameter `t`.