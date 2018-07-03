require(["jquery", "d3", "topojson"], function ($, d3, topojson) {
    "use strict";
    $(document).ready(function () {

        var width = 800;
        var height = 600;
        var lines = [];
        var svg = d3.select("#chart")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        var map = svg.append("g").attr("id", "map");
        var places = svg.append("g").attr("id", "places");
        var wind = svg.append("g").attr("id", "wind");

        var projection = d3.geo.mercator()
            .center([126.9895, 37.5651])
            .scale(145723)
            .translate([width / 2, height / 2]);
        var path = d3.geo.path().projection(projection);


        d3.json("/static/windows/seoul_topo.json", function (error, data) {
            var features = topojson.feature(data, data.objects.seoul_municipalities_geo).features;
            console.log(features);
            map.selectAll("path")
                .data(features)
                .enter().append("path")
                .attr("class", function (d) {
                    return "municipality c" + d.properties.code
                })
                .attr("d", path);

            map.selectAll("text")
                .data(features)
                .enter().append("text")
                .attr("transform", function (d) {
                    return "translate(" + path.centroid(d) + ")";
                })
                .attr("dy", ".35em")
                .attr("class", "municipality-label")
                .text(function (d) {
                    return d.properties.name;
                })
        });

        d3.csv("/static/windows/data/observatory.csv", function (data) {
            places.selectAll("circle")
                .data(data)
                .enter().append("circle")
                .attr("cx", function (d) {
                    return projection([d.lon, d.lat])[0];
                })
                .attr("cy", function (d) {
                    return projection([d.lon, d.lat])[1];
                })
                .attr("r", 4);
        });

        // http://prcweb.co.uk/making-the-uk-wind-chart/
        function lineAnimate(selection) {
            selection
                .attr({
                    x2: function (d) {
                        return d.x0
                    },
                    y2: function (d) {
                        return d.y0
                    }
                })
                .style('opacity', 0)
                .transition()
                .ease('linear')
                .duration(function (d) {
                    return d.duration;
                })
                .delay(function (d) {
                    return d.delay;
                })
                .attr({
                    x2: function (d) {
                        return d.x1
                    },
                    y2: function (d) {
                        return d.y1
                    }
                })
                .style('opacity', 0.8)
                .transition()
                .duration(1000)
                .style('opacity', 0.1)
                .each('end', function () {
                    d3.select(this).call(lineAnimate)
                });

        }

        function toRad(deg) {
            var out_deg = [];
            for (var i = 0; i < deg.length; i++) {
                out_deg.push(deg[i] * Math.PI / 180.0);
            }
            return out_deg;
        }

        function toDeg(rad) {
            var out_rad = [];
            for (var i = 0; i < rad.length; i++) {
                out_rad.push(rad[i] / Math.PI * 180.0);
            }
            return out_rad;
        }

        function lonLatFromLonLatDistanceAndBearing(lon, lat, d, brng) {
            // Formulae from http://www.movable-type.co.uk/scripts/latlong.html
            // brg in radians, d in km
            var R = 6371; // Earth's radius in km
            var lon1 = toRad(lon), lat1 = toRad(lat);
            //var lat2 = Math.asin( Math.sin(lat1)*Math.cos(d/R) + Math.cos(lat1)*Math.sin(d/R)*Math.cos(brng) );
            var lat2 = [];
            for (var i = 0; i < lat1.length; i++) {
                lat2.push(Math.asin(Math.sin(lat1[i]) * Math.cos(d[i] / R) + Math.cos(lat1[i]) * Math.sin(d[i] / R) * Math.cos(brng[i] * Math.PI / 180.0)))
            }
            var lon2 = [];
            //var lon2 = lon1 + Math.atan2(Math.sin(toRad(brng))*Math.sin(d/R)*Math.cos(lat1), Math.cos(d/R)-Math.sin(lat1)*Math.sin(lat2));
            for (var i = 0; i < lat1.length; i++) {
                lon2.push(lon1[i] + Math.atan2(Math.sin(brng[i] * Math.PI / 180.0) * Math.sin(d[i] / R) * Math.cos(lat1[i]), Math.cos(d[i] / R) - Math.sin(lat1[i]) * Math.sin(lat2[i])));
            }

            return [toDeg(lon2), toDeg(lat2)];
        }

        function init() {
            d3.csv("/static/windows/data/data_wind.csv", function (data) {
                var lat = data.map(function (d) {
                    return d.lat
                });
                var lon = data.map(function (d) {
                    return d.lng
                });
                var speed = data.map(function (d) {
                    return d.windspeed
                });
                var angle = data.map(function (d) {
                    return d.angle
                });

                var lonLat1 = lonLatFromLonLatDistanceAndBearing(lon, lat, speed, angle);


                for (var i = 0; i < lon.length; i++) {
                    var x0y0 = projection([lon[i], lat[i]]);
                    var x1y1 = projection([lonLat1[0][i], lonLat1[1][i]]);
                    var line = {
                        x0: x0y0[0],
                        y0: x0y0[1],
                        x1: x1y1[0],
                        y1: x1y1[1],
                        s: 1.2 * speed[i],
                        duration: 8000 / speed[i],
                        delay: Math.random() * 1000
                    };
                    lines.push(line);
                }
                wind.selectAll('line')
                    .data(lines)
                    .enter()
                    .append("line")
                    .attr({
                        x1: function (d) {
                            return d.x0
                        },
                        y1: function (d) {
                            return d.y0
                        }
                    })
                    .call(lineAnimate);
            });
        }

        init();

        /*
         var chart = L.map('chart');
         var pminfo_data = [];
         d3.json("/static/pminfo.json", function(error, pminfo) {
         for (var i=0; i<pminfo.DATA.length; i++) {
         var x0y0 = projection([pminfo.DATA[i].lat, pminfo.DATA[i].lng]);
         var temp = new Array(x0y0[0], x0y0[1], pminfo.DATA[i].PM25);
         pminfo_data.push(temp);
         }
         console.log(pminfo_data);
         var heat = L.heatLayer(pminfo_data, {radious: 10000}).addTo(chart);
         });
         */
    });
});





