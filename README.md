Project status - Current work in progress at Alpha stage.

# AIXMGeo

AIXMGeo is an AIXM wrapper for [KMLPlus](https://github.com/MHenderson1988/kmlplus) which supports the creation of a
curved and 'floating' objects in KML.

AIXMGeo parses a valid, well-formed, AIXM file and outputs geographic information to a .KML file. The .KML file can be
opened in Google Earth or other mapping software.

AIXMGeo is currently only tested with AIXM 5.1 however it should also work with AIXM 5.1.1.

## Supported AIXM features

* Airspace
* NavaidComponent
* RouteSegment
* AirportHeliport (ARP)
* DesignatedPoint

## Use

```
AixmGeo(aixm_file_path, kml_output_path, kml_file_name).build_kml()
```

