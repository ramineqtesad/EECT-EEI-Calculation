// eei_dashboard.js
// Google Earth Engine script for real-time EEI monitoring dashboard

// Import datasets
var landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(ee.Geometry.Point(45.3, 37.7));
var modis = ee.ImageCollection('MODIS/006/MOD09GA').filterBounds(ee.Geometry.Point(45.3, 37.7));

// Define Lake Urmia region
var lakeUrmia = ee.Geometry.Polygon([
  [[45.0, 37.4], [45.6, 37.4], [45.6, 37.8], [45.0, 37.8], [45.0, 37.4]]
]);

// Calculate salinity (proxy using NDWI)
var calculateSalinity = function(image) {
  var ndwi = image.normalizedDifference(['sur_refl_b03', 'sur_refl_b05']).rename('NDWI');
  return image.addBands(ndwi);
};

// Filter and process data (1990–2024)
var dataset = landsat.merge(modis).filterDate('1990-01-01', '2024-12-31');
var salinity = dataset.map(calculateSalinity).select('NDWI').mean().clip(lakeUrmia);

// Mock biodiversity and energy flow (replace with actual data if available)
var biodiversity = ee.Image.constant(1.1); // Example: Shannon Index for 2024
var energyFlow = ee.Image.constant(1200); // Example: MJ/m² for 2024

// Calculate EEI
var eei = biodiversity.add(salinity.multiply(0.5)).add(biodiversity.multiply(0.3)).add(energyFlow.multiply(0.2/1200*10));

// Create dashboard UI
var panel = ui.Panel({style: {width: '400px'}});
panel.add(ui.Label('EEI Monitoring Dashboard for Lake Urmia'));

// Add time-series chart
var chart = ui.Chart.image.series(dataset.select('NDWI'), lakeUrmia, ee.Reducer.mean(), 30)
  .setOptions({
    title: 'Salinity Trend (NDWI Proxy, 1990–2024)',
    hAxis: {title: 'Year'},
    vAxis: {title: 'NDWI'}
  });
panel.add(chart);

// Add EEI display
panel.add(ui.Label('EEI (2024): ' + eei.getInfo()));

// Add migration data (mock)
var migration = ee.Image.constant(0.3); // Example: EEI_urban impact
panel.add(ui.Label('Migration Impact on EEI_urban: 0.3'));

// Add map
var map = ui.Map();
map.centerObject(lakeUrmia, 10);
map.addLayer(salinity, {min: -0.5, max: 0.5, palette: ['blue', 'white', 'red']}, 'Salinity');
map.addLayer(eei, {min: 0, max: 5, palette: ['green', 'yellow', 'red']}, 'EEI');
panel.add(map);

ui.root.add(panel);

// Export dashboard link
print('Dashboard URL:', ui.root.getUrl());
