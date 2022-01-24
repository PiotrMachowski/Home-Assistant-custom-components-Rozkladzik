[![HACS Default][hacs_shield]][hacs]
[![GitHub Latest Release][releases_shield]][latest_release]
[![GitHub All Releases][downloads_total_shield]][releases]
[![Buy me a coffee][buy_me_a_coffee_shield]][buy_me_a_coffee]
[![PayPal.Me][paypal_me_shield]][paypal_me]


[hacs_shield]: https://img.shields.io/static/v1.svg?label=HACS&message=Default&style=popout&color=green&labelColor=41bdf5&logo=HomeAssistantCommunityStore&logoColor=white
[hacs]: https://hacs.xyz/docs/default_repositories

[latest_release]: https://github.com/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/releases/latest
[releases_shield]: https://img.shields.io/github/release/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik.svg?style=popout

[releases]: https://github.com/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/releases
[downloads_total_shield]: https://img.shields.io/github/downloads/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/total

[buy_me_a_coffee_shield]: https://img.shields.io/static/v1.svg?label=%20&message=Buy%20me%20a%20coffee&color=6f4e37&logo=buy%20me%20a%20coffee&logoColor=white
[buy_me_a_coffee]: https://www.buymeacoffee.com/PiotrMachowski

[paypal_me_shield]: https://img.shields.io/static/v1.svg?label=%20&message=PayPal.Me&logo=paypal
[paypal_me]: https://paypal.me/PiMachowski

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

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

This integration can be installed using HACS.
To do it search for `Rozkładzik` in *Integrations* section.

### Manual

To install this integration manually you have to download [*rozkladzik.zip*](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/releases/latest/download/rozkladzik.zip) and extract its contents to `config/custom_components/rozkladzik` directory:
```bash
mkdir -p custom_components/rozkladzik
cd custom_components/rozkladzik
wget https://github.com/PiotrMachowski/Home-Assistant-custom-components-Rozkladzik/releases/latest/download/rozkladzik.zip
unzip rozkladzik.zip
rm rozkladzik.zip
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
  * This integration is available in [*HACS*](https://github.com/custom-components/hacs/).
## FAQ

* **How to get values for configuration parameters?**

  To find out values for configuration parameters follow the following steps: 
  - Go to [rozkladzik.pl](https://www.rozkladzik.pl) and find desired stop.
  - Activate developer tools using `[F12]` button.
  - Click on chosen stop and in network tab look for call to `https://www.rozkladzik.pl/<name_of_city>/timetable.txt?...` URL
  - Value for `stops_group_mode` is determined by value of query parameter `c`. If it is equal to `bsa` you have to enable group mode.
  - Value for `city` comes from `<name_of_city>` path fragment.
  - Value for `id` comes from query parameter `t` or `b` for group mode.

<a href="https://www.buymeacoffee.com/PiotrMachowski" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
<a href="https://paypal.me/PiMachowski" target="_blank"><img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg" border="0" alt="PayPal Logo" style="height: auto !important;width: auto !important;"></a>
