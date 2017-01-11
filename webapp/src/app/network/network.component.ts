import { Component, AfterViewInit, ViewChild, Output, EventEmitter } from '@angular/core';
import * as d3 from 'd3';
import * as ejs from 'ejs';

import { constructGraph } from "./graph";

@Component({
  selector: 'app-network',
  templateUrl: './network.component.html',
  styleUrls: ['./network.component.css', './github-pandoc.css']
})
export class NetworkComponent implements AfterViewInit {

  @Output() public title = new EventEmitter<string>();
  @Output() public text = new EventEmitter<string>();
  @ViewChild('net') public net;
  repo = 'https://github.com/mschuwalow/StudDP'; // TODO: map to url
  constructor() { }

  ngAfterViewInit() {

    var w = window.innerWidth * 0.68 * 0.95;
    var h = Math.ceil(w * 0.7);
    let size = 120; // node size
    var oR = 0;
    var nTop = 0;

    let elem = this.net.nativeElement;

    var svg = d3.select(elem).append("svg")
      .attr("width", w)
      .attr("height", h)
      .on("mouseleave", function() { return resetBubbles(); });

    let g = svg.append('g');

    // [1] DEV [2] HW [3] EDU [4] DOCS [5] WEB [6] DATA [7] OTHER
    const DEV = 1, HW = 2, EDU = 3, DOCS = 4, WEB = 5, DATA = 6, OTHER = 7;
    const NAMES = ["DEV", "HW", "EDU", "DOCS", "WEB", "DATA", "OTHER"];

    interface NetworkDebugger {
      // CONVENIENCE
      names: string[]; // map numbers to category names
      // NETWORK DATA
      decision: number;
      // CNN
      softmaxCNN: number[];
      outputCNN: number;
      filtersCNN: number[]; // filter sizes as in settings.py

      // parameters
      sequenceLength: number;
      embeddingSize: number;
      // FFN

      // INPUT DATA
      readme: string;
      readmePreprocessed: string;
      contributors: number;
      issues: number;
      branches: number;
      forks: number;
      stars: number;
      pullRequests: number;
      subscribers: number;
      commits: number;
      // as unix time
      commitTimes: number[];
      startTime: number;
      updateTime: number;
    }
    let data = {

    }; // TODO suck it out of maxim

    d3.json("/assets/network.json", (error, root: any) => {
      console.log(error);
      let hierarchy = d3.hierarchy(root);
      let tree = d3.tree()
        .separation(function(a, b) { return a.parent == b.parent ? 1 : 2; })
        .nodeSize([120, 120])
        (hierarchy);

      var node = g.selectAll(".node")
        .data(tree.descendants().slice(1))
        .enter().append("g")
        .attr("class", function(d) { return "node" + (d.children ? " node--internal" : " node--leaf"); })
        .attr("transform", function(d) {
          // y = level in tree
          let y = (d.y - 0.5) * h; // place in mid-screen, at page {level}
          // x = index (children), 0 = mid
          let x = (w / 2) + d.x * size;
          return "translate(" + d.y + "," + d.x + ")";
        })
        .each((d: any) => console.info(`${d.data.name} at (${d.x}, ${d.y})`));

      node.on('mouseover', (d: any) => {
        this.title.emit(d.data.name);
        let template = d.data.description;
        let text = "";
        if (template)
          text = ejs.render(template, data);
        this.text.emit(text);
      });

      //   node.on('mouseout', () => {
      //     this.title.emit(null);
      //     this.text.emit(null);
      //   });

      let zoom = d3.zoom().on('zoom', function() {
        g.attr('transform', d3.event.transform);
      });
      svg.call(zoom as any);

      function zoomOnLevel(level) {
        let x = level.map(node => node.x);
        let y = level.map(node => node.y);
        let minX = Math.min.apply(null, x);
        let minY = Math.min.apply(null, y);
        let maxX = Math.max.apply(null, x);
        let maxY = Math.max.apply(null, y);
        let tr = g.attr('transform');
        console.log(`before: ${tr}`)
        svg.call(zoom.transform, d3.zoomIdentity.translate(minX, minY).scale(d3.zoomTransform(g.node() as Element).k));
        tr = g.attr('transform');
        console.log(`after: ${tr}`)
        let vars: any = {};
        vars['extent'] = [[minX, minY], [maxX, maxY]];
        vars['level'] = level;
        vars['group'] = g;
        vars['zoom'] = zoom;
        console.dir(vars);
      };
      node.on('click', function(d) {

        if (d.children && d.children.length >= 1)
          zoomOnLevel(d.children);
      });
      //zoomOnLevel(tree.children[0]);

      node.each(function(d: any, i) {
        let elem = this;
        if (d.data.template)
          d3.request(`/assets/${d.data.template}.svg`)
            .mimeType("application/json")
            .response(xhr => xhr.responseText)
            .get(function(template) {
              elem.innerHTML = ejs.render(template, data);
            });
        else
          elem.innerHTML = `<text>${d.data.name}</text>`;
      });

    });
    function resetBubbles() {
      return;
    }

    window.onresize = resetBubbles;
  }
  //
  //   nTop = root.children.length;
  //   oR = w / (1 + 3 * nTop);
  //
  //   h = Math.ceil(w / nTop * 2);
  //   //svgContainer.style("height", h + "px");
  //
  //   var colVals = d3.scaleOrdinal(d3.schemeCategory10);
  //
  //   bubbleObj.append("circle")
  //     .attr("class", "topBubble")
  //     .attr("id", function(d, i) { return "topBubble" + i; })
  //     .attr("r", function(d) { return oR; })
  //     .attr("cx", function(d, i) { return oR * (3 * (1 + i) - 1); })
  //     .attr("cy", (h + oR) / 3)
  //     .style("fill", function(d, i: any) { return colVals(i); }) // #1f77b4
  //     .style("opacity", 0.3)
  //     .on("mouseover", function(d, i) { return activateBubble(d, i); });
  //
  //
  //   bubbleObj.append("text")
  //     .attr("class", "topBubbleText")
  //     .attr("x", function(d, i) { return oR * (3 * (1 + i) - 1); })
  //     .attr("y", (h + oR) / 3)
  //     .style("fill", function(d, i: any) { return colVals(i); }) // #1f77b4
  //     .attr("font-size", 30)
  //     .attr("text-anchor", "middle")
  //     .attr("dominant-baseline", "middle")
  //     .attr("alignment-baseline", "middle")
  //     .text(function(d: any) { return d.name })
  //     .on("mouseover", function(d, i) { return activateBubble(d, i); });
  //
  //
  //   for (var iB = 0; iB < nTop; iB++) {
  //     var childBubbles = svg.selectAll(".childBubble" + iB)
  //       .data(root.children[iB].children)
  //       .enter().append("g");
  //
  //     //var nSubBubble = Math.floor(root.children[iB].children.length/2.0);
  //
  //     childBubbles.append("circle")
  //       .attr("class", "childBubble" + iB)
  //       .attr("id", function(d, i) { return "childBubble_" + iB + "sub_" + i; })
  //       .attr("r", function(d) { return oR / 3.0; })
  //       .attr("cx", function(d, i) { return (oR * (3 * (iB + 1) - 1) + oR * 1.5 * Math.cos((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("cy", function(d, i) { return ((h + oR) / 3 + oR * 1.5 * Math.sin((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("cursor", "pointer")
  //       .style("opacity", 0.5)
  //       .style("fill", "#eee")
  //       .on("click", function(d: any, i) {
  //         window.open(d.address);
  //       })
  //       .on("mouseover", function(d: any, i) {
  //         //window.alert("say something");
  //         var noteText = "";
  //         if (d.note == null || d.note == "") {
  //           noteText = d.address;
  //         } else {
  //           noteText = d.note;
  //         }
  //         d3.select("#bubbleItemNote").text(noteText);
  //       })
  //       .append("svg:title")
  //       .text(function(d: any) { return d.address; });
  //
  //     childBubbles.append("text")
  //       .attr("class", "childBubbleText" + iB)
  //       .attr("x", function(d, i) { return (oR * (3 * (iB + 1) - 1) + oR * 1.5 * Math.cos((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("y", function(d, i) { return ((h + oR) / 3 + oR * 1.5 * Math.sin((i - 1) * 45 / 180 * 3.1415926)); })
  //       .style("opacity", 0.5)
  //       .attr("text-anchor", "middle")
  //       .style("fill", function(d, i) { return colVals(iB as any); }) // #1f77b4
  //       .attr("font-size", 6)
  //       .attr("cursor", "pointer")
  //       .attr("dominant-baseline", "middle")
  //       .attr("alignment-baseline", "middle")
  //       .text(function(d: any) { return d.name })
  //       .on("click", function(d: any) {
  //         window.open(d.address);
  //       });
  //
  //   }
  //
  //
  // });
  //
  //   w = window.innerWidth * 0.68 * 0.95;
  //   oR = w / (1 + 3 * nTop);
  //
  //   h = Math.ceil(w / nTop * 2);
  //   //svgContainer.style("height", h + "px");
  //
  //   mainNote.attr("y", h - 15);
  //
  //   svg.attr("width", w);
  //   svg.attr("height", h);
  //
  //   d3.select("#bubbleItemNote").text("D3.js bubble menu developed by Shipeng Sun (sunsp.gis@gmail.com), Institute of Environment, University of Minnesota, and University of Springfield, Illinois.");
  //
  //   var t = svg.transition()
  //     .duration(650);
  //
  //   t.selectAll(".topBubble")
  //     .attr("r", function(d) { return oR; })
  //     .attr("cx", function(d, i) { return oR * (3 * (1 + i) - 1); })
  //     .attr("cy", (h + oR) / 3);
  //
  //   t.selectAll(".topBubbleText")
  //     .attr("font-size", 30)
  //     .attr("x", function(d, i) { return oR * (3 * (1 + i) - 1); })
  //     .attr("y", (h + oR) / 3);
  //
  //   for (var k = 0; k < nTop; k++) {
  //     t.selectAll(".childBubbleText" + k)
  //       .attr("x", function(d, i) { return (oR * (3 * (k + 1) - 1) + oR * 1.5 * Math.cos((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("y", function(d, i) { return ((h + oR) / 3 + oR * 1.5 * Math.sin((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("font-size", 6)
  //       .style("opacity", 0.5);
  //
  //     t.selectAll(".childBubble" + k)
  //       .attr("r", function(d) { return oR / 3.0; })
  //       .style("opacity", 0.5)
  //       .attr("cx", function(d, i) { return (oR * (3 * (k + 1) - 1) + oR * 1.5 * Math.cos((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("cy", function(d, i) { return ((h + oR) / 3 + oR * 1.5 * Math.sin((i - 1) * 45 / 180 * 3.1415926)); });
  //
  //   }
  // }
  //
  //
  // function activateBubble(d, i) {
  //   // increase this bubble and decrease others
  //   var t = svg.transition()
  //     .duration(d3.event.altKey ? 7500 : 350);
  //
  //   t.selectAll(".topBubble")
  //     .attr("cx", function(d, ii) {
  //       if (i == ii) {
  //         // Nothing to change
  //         return oR * (3 * (1 + ii) - 1) - 0.6 * oR * (ii - 1);
  //       } else {
  //         // Push away a little bit
  //         if (ii < i) {
  //           // left side
  //           return oR * 0.6 * (3 * (1 + ii) - 1);
  //         } else {
  //           // right side
  //           return oR * (nTop * 3 + 1) - oR * 0.6 * (3 * (nTop - ii) - 1);
  //         }
  //       }
  //     })
  //     .attr("r", function(d, ii) {
  //       if (i == ii)
  //         return oR * 1.8;
  //       else
  //         return oR * 0.8;
  //     });
  //
  //   t.selectAll(".topBubbleText")
  //     .attr("x", function(d, ii) {
  //       if (i == ii) {
  //         // Nothing to change
  //         return oR * (3 * (1 + ii) - 1) - 0.6 * oR * (ii - 1);
  //       } else {
  //         // Push away a little bit
  //         if (ii < i) {
  //           // left side
  //           return oR * 0.6 * (3 * (1 + ii) - 1);
  //         } else {
  //           // right side
  //           return oR * (nTop * 3 + 1) - oR * 0.6 * (3 * (nTop - ii) - 1);
  //         }
  //       }
  //     })
  //     .attr("font-size", function(d, ii) {
  //       if (i == ii)
  //         return 30 * 1.5;
  //       else
  //         return 30 * 0.6;
  //     });
  //
  //   var signSide = -1;
  //   for (var k = 0; k < nTop; k++) {
  //     signSide = 1;
  //     if (k < nTop / 2) signSide = 1;
  //     t.selectAll(".childBubbleText" + k)
  //       .attr("x", function(d, i) { return (oR * (3 * (k + 1) - 1) - 0.6 * oR * (k - 1) + signSide * oR * 2.5 * Math.cos((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("y", function(d, i) { return ((h + oR) / 3 + signSide * oR * 2.5 * Math.sin((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("font-size", function() {
  //         return (k == i) ? 12 : 6;
  //       })
  //       .style("opacity", function() {
  //         return (k == i) ? 1 : 0;
  //       });
  //
  //     t.selectAll(".childBubble" + k)
  //       .attr("cx", function(d, i) { return (oR * (3 * (k + 1) - 1) - 0.6 * oR * (k - 1) + signSide * oR * 2.5 * Math.cos((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("cy", function(d, i) { return ((h + oR) / 3 + signSide * oR * 2.5 * Math.sin((i - 1) * 45 / 180 * 3.1415926)); })
  //       .attr("r", function() {
  //         return (k == i) ? (oR * 0.55) : (oR / 3.0);
  //       })
  //       .style("opacity", function() {
  //         return (k == i) ? 1 : 0;
  //       });
  //   }
  // }


}
