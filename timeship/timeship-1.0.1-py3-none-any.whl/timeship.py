# -*- coding: utf-8 -*-

import os
import re
import datetime

import json
from collections import defaultdict
import numpy as np


html = """<!DOCTYPE html>
<!--the html code was originally released by Mike Bostock under gpl-3.0 here: https://gist.github.com/mbostock/4348373-->
<meta charset="utf-8">
<style>
    path {
        stroke: #fff;
    }
</style>

<body>
    <script src="https://d3js.org/d3.v4.min.js"></script>
    <script>
        var data = <% data_json %>
        var width = 960,
            height = 700,
            radius = (Math.min(width, height) / 2) - 10;
        var formatNumber = d3.format(",d");
        var x = d3.scaleLinear()
            .range([0, 2 * Math.PI]);
        var y = d3.scaleSqrt()
            .range([0, radius]);
        var color = d3.scaleOrdinal(d3.schemeCategory20);
        var partition = d3.partition();
        var arc = d3.arc()
            .startAngle(function(d) {
                return Math.max(0, Math.min(2 * Math.PI, x(d.x0)));
            })
            .endAngle(function(d) {
                return Math.max(0, Math.min(2 * Math.PI, x(d.x1)));
            })
            .innerRadius(function(d) {
                return Math.max(0, y(d.y0));
            })
            .outerRadius(function(d) {
                return Math.max(0, y(d.y1));
            });
        var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(" + width / 2 + "," + (height / 2) + ")");

        data = d3.hierarchy(data);
        data.sum(function(d) {
            return d.value;
        });
        svg.selectAll("path")
            .data(partition(data).descendants())
            .enter().append("path")
            .attr("d", arc)
            .style("fill", function(d) {
                return color((d.children ? d : d.parent).data.name);
            })
            .on("click", click)
            .append("title")
            .text(function(d) {
                return d.data.name + "\\n" + formatNumber(d.value);
            });

        function click(d) {
            svg.transition()
                .duration(750)
                .tween("scale", function() {
                    var xd = d3.interpolate(x.domain(), [d.x0, d.x1]),
                        yd = d3.interpolate(y.domain(), [d.y0, 1]),
                        yr = d3.interpolate(y.range(), [d.y0 ? 20 : 0, radius]);
                    return function(t) {
                        x.domain(xd(t));
                        y.domain(yd(t)).range(yr(t));
                    };
                })
                .selectAll("path")
                .attrTween("d", function(d) {
                    return function() {
                        return arc(d);
                    };
                });
        }
        d3.select(self.frameElement).style("height", height + "px");
    </script>
</body>
"""


class rec_defaultdict(defaultdict):

    def __init__(self, *args, **kwargs):
        self.value = None
        super(rec_defaultdict, self).__init__(self.__class__, *args, **kwargs)

    def __getitem__(self, key):
        if '/' not in key:
            return super(rec_defaultdict, self).__getitem__(key)
        else:
            id, key = key.split("/", 1)
            return self[id][key]

    def set_child_times(self):
        if len(self.keys()) == 0:
            self.value.child_time = 0
            return self.value.total_time()
        else:
            child_time = sum(
                self[key].set_child_times() for key in self.keys()
            )
            if self.value:
                self.value.child_time = child_time
            return child_time

    def to_dict(self, id=None):
        self.set_child_times()
        _ = {}
        if id is None:
            _.update({"name": "root"})
        else:
            _.update({"name": id})
        if self.value:
            _.update({"value": self.value.anchor_time()})
        if len(self.keys()) > 0:
            _.update({
                "children": [
                    self[name].to_dict(name) for name in self.keys()
                ],
            })
        return _

    def to_array(self):
        if len(self.keys()) == 0:
            return np.array(self.value)
        else:
            _ = np.array([self[key].to_array() for key in self.keys()])
            if self.value:
                _ = np.concatenate(
                    (
                        np.array([self.value.starts]),
                        _,
                    ),
                    axis=0
                )
            return _

    def to_list(self):
        list = []
        if self.value:
            list.append(self.value)
        if len(self.keys()) > 0:
            for key in self.keys():
                [list.append(item) for item in self[key].to_list()]
        return list


class Anchor():
    def __init__(self, id):
        self.id = id
        self.starts, self.stops = [], []
        self.is_active = False
        self.child_time = 0

    def __enter__(self):
        self.start()
        current_scope = get_current_scope()
        set_current_scope(
            "/".join([current_scope, self.id]) if len(current_scope) > 0 else self.id
        )
        current_scope = get_current_scope()
        anchors[current_scope].value = self
        return self

    def __exit__(self, *args):
        current_scope = get_current_scope()
        if current_scope == self.id:
            set_current_scope("")
        else:
            set_current_scope(current_scope.rsplit("/" + self.id, 1)[0])
        self.stop()

    def start(self):
        self.starts.append(datetime.datetime.now())
        self.is_active = True

    def stop(self):
        self.stops.append(datetime.datetime.now())
        self.is_active = False

    def total_time(self):
        total_runtime = sum([
            (stop - start).total_seconds()
            for (stop, start) in zip(self.stops, self.starts)
        ])
        return total_runtime

    def anchor_time(self):
        anchor_runtime = sum([
            (stop - start).total_seconds()
            for (stop, start) in zip(self.stops, self.starts)
        ]) - self.child_time
        return anchor_runtime


def get_current_scope():
    global current_scope
    return current_scope


def set_current_scope(id):
    global current_scope
    current_scope = id


def anchor(id=None, release=False):
    anchor_list = anchors.to_list()
    if id is None:
        [anchor.stop() for anchor in anchor_list if anchor.is_active]
    elif id in [anchor.id for anchor in anchor_list]:
        if release:
            anchors[id].value.stop()
        else:
            anchors[id].value.start()
    else:
        anchor = Anchor(id)
        anchor.start()
        anchors[id].value = anchor


def plot(dir='timeship'):
    global html
    # make directory
    os.makedirs(dir, exist_ok=True)

    # write data into html
    dictified_data = anchors.to_dict()
    data_json = json.dumps(dictified_data, indent=4)
    html = re.sub(r'<% data_json %>', data_json, html)

    # write html
    html_path = os.path.join(dir, "index.html")
    with open(html_path, "w") as file:
        file.write(html)


current_scope = ""
anchors = rec_defaultdict()
