# Pelagic Checklist Filters

This repo is for getting pelagic checklists from the pelagic polygons on eBird.


## How to get these checklists

To do this, first go into Google Earth. Load up the pelagic file, `arb_poly_ocean.kmz`. Click on a polygon you want, and export it as a .kml, not as a .kmz file.

Go into the file in Sublime. Ensure that:

```
          </LinearRing>
          </innerBoundaryIs>
        <innerBoundaryIs>
          <LinearRing>
            <coordinates>
```

Google Earth Pro and Google Earth online both have a bug, where they export .kml files that have multiple `LinearRing` objects in a single `innerBoundaryIs` object. That's invalid KML, and it'll result in only a single - the last - hole in the polygon. To get around this, run a quick script to add more `innerBoundaryIs` tags between `LinearRing`s. Or, do it manually.

The Python script provided will convert your .kml file into a .geojson, and then filter it appropriately. You need to request and download the eBird data for the appropriate region, and have it locally available. 


Then you can run the ebd data. It'll output a .csv with the checklists you want to look at for that pelagic region, minus the holes.

You'll wan to run something like this:

```
$ python pelagic.py baffin.kml baffin.geojson ebd_GL_smp_relNov-2023/ebd_GL_smp_relNov-2023.txt baffin.csv
```

Where Baffin is the name for the .geojson file you're going to export as a byproduct, and the output file is `baffin.csv`.

### kml to geojson

Alternatively, you can install and then run ogr2ogr on the kml file to make a geojson.

```
$ ogr2ogr -f GeoJSON baffin.geojson GL--pelagic-Baffin.kml
```

## Contribute

Feel free. I know this guide isn't perfect.

## License

MIT.