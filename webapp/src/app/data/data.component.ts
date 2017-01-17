import { Component, AfterViewInit, ViewChild, Input, Output, EventEmitter } from '@angular/core';
import * as d3 from 'd3';
import { Repo } from '../repo/repo.component';


@Component({
  selector: 'app-data',
  templateUrl: './data.component.html',
  styleUrls: ['./data.component.css']
})
export class DataComponent implements AfterViewInit {

  @ViewChild('plot') plot;
  @ViewChild('data') datapoints;

  public categories = ["NumberOfContributors", /*"NumberOfIssues", */"Branches", "Forks", "Stars", "Pulls", "Subscribers", "NumberOfCommits", "Category"];
  public categoryLabels = ["Contributors", /*"Issues", */ "Branches", "Forks", "Stars", "Pulls", "Subscribers", "Commits", "Category"];

  @Input() xAxis: string = 'Stars';
  @Input() yAxis: string = 'Branches';

  @Output() dataLoaded = false;
  @Output() width = 800;
  @Output() height = 600;
  @Output() colors = d3.scaleOrdinal(d3.schemeCategory10);
  @Output() repo = new EventEmitter<Repo>();
  @Output() xStart: number;
  @Output() xEnd: number;
  @Output() yStart: number;
  @Output() yEnd: number;
  @Output() screenEnd = [this.width, this.height];
  @Output() screenStart = [0, 0];
  @Output() normalXScale: d3.ScaleLinear<number, number>;
  @Output() normalYScale: d3.ScaleLinear<number, number>;
  @Output() scale: number;

  size = 5;

  private data: Repo[];

  constructor() { }

  public resetScale() {
    const row = attr => this.data.map(d => d[attr]);
    const domain = data => [Math.min(...data), Math.max(...data)];
    const xData = row(this.xAxis);
    const yData = row(this.yAxis);
    [this.xStart, this.xEnd] = domain(xData);
    [this.yStart, this.yEnd] = domain(yData);

    this.normalXScale = d3.scaleLinear()
      .domain([this.xStart, this.xEnd])
      .range([this.size, this.width - this.size]);

    this.normalYScale = d3.scaleLinear()
      .domain([this.yStart, this.yEnd])
      .range([this.size, this.height - this.size]);
  }

  ngAfterViewInit() {
    let number = 6;
    this.data = [];
    let done = () => {
      this.resetScale();
      this.dataLoaded = true;
      this.draw();
    };
    for (let type of ['dev', 'edu', 'homework', 'data', 'web', 'docs']) {
      d3.json(`assets/data/${type}_full.json`, (error, data) => {
        if (error) {
          throw new Error("Something went wrong" + error);
        }
        this.data = this.data.concat(data as Repo[]);
        number--;
        if (number == 0) {
          done();
        }
      })
    }
  }

  draw() {
    if (!this.dataLoaded) return;

    const plot = d3.select(this.plot.nativeElement);
    const datapoints = d3.select(this.datapoints.nativeElement);

    const xDomain = [this.xStart, this.xEnd];
    const yDomain = [this.yStart, this.yEnd];

    const xScale = d3.scaleLinear()
      .domain(xDomain)
      .range([this.screenStart[0], this.screenEnd[0]]);

    const yScale = d3.scaleLinear()
      .domain(yDomain)
      .range([this.screenStart[1], this.screenEnd[1]]);

    let xValues = xScale.ticks();
    if (xValues.length == 0) xValues = [xDomain[0]];

    let yValues = yScale.ticks();
    if (yValues.length == 0) yValues = [yDomain[0]];

    const fontSize = 10 * (1 / this.scale);

    const xLabel = datapoints.selectAll('text.xLabel').data(xValues);
    xLabel.exit().remove();
    xLabel.enter()
      .append('text').classed('xLabel', true)
      .merge(xLabel)
      .text(d => d)
      .attr('x', (d) => xScale(d))
      .attr('y', this.screenEnd[1] - fontSize)
      .attr('font-size', fontSize)
      .attr('text-align', 'start');

    const yLabel = datapoints.selectAll('text.yLabel').data(yValues);
    yLabel.exit().remove();
    yLabel.enter()
      .append('text').classed('yLabel', true)
      .merge(yLabel)
      .text(d => d)
      .attr('y', (d) => yScale(d))
      .attr('x', this.screenStart[0] + fontSize)
      .attr('font-size', fontSize)
      .attr('text-align', 'start');

    const self = this;
    const zoomed = function() {
      const tr = d3.zoomTransform(this);
      datapoints.attr('transform', tr.toString());
      self.scale = tr.k;
      self.screenStart = tr.invert([0, 0]);
      self.screenEnd = tr.invert([self.width, self.height]);
      let domainStart = [self.normalXScale.invert(self.screenStart[0]), self.normalYScale.invert(self.screenStart[1])];
      let domainEnd = [self.normalXScale.invert(self.screenEnd[0]), self.normalYScale.invert(self.screenEnd[1])];
      console.log(`screen: ${self.screenStart} - ${self.screenEnd}`);
      console.log(`domain: ${domainStart} - ${domainEnd}`);
      [self.xStart, self.yStart] = domainStart;
      [self.xEnd, self.yEnd] = domainEnd;
      //   [self.xStart, self.xEnd] = [Math.min(self.xStart, self.xEnd), Math.max(self.xStart, self.xEnd)];
      //   [self.yStart, self.yEnd] = [Math.min(self.yStart, self.yEnd), Math.max(self.yStart, self.yEnd)];
      self.draw();
    };
    const zoom = d3.zoom().on('zoom', zoomed);
    plot.call(zoom);
    const repos = datapoints.selectAll('g.repo').data(this.data);

    repos.exit().remove();

    const enter = repos.enter()
      .append('g')
      .classed('repo', true)
      .on('mouseover', (repo: Repo) => {
        this.repo.emit(repo);
      });
    enter.append('circle');
    repos.merge(enter)
      .select('circle')
      .attr('cx', d => xScale(d[this.xAxis]))
      .attr('cy', d => yScale(d[this.yAxis]))
      .attr('r', () => this.size)
      .attr('fill', (d: Repo) => this.colors(d.Category))
      .attr('stroke', 'black');


    // const voronoi = d3.voronoi()
    //   .x(d => xScale(d[this.xAxis]))
    //   .y(d => yScale(d[this.yAxis]))
    //   .extent([[-1, -1], [this.width + 1, this.height + 1]]);
    //
    // let cell = repos.merge(enter).append("path")
    //   .data(voronoi.polygons(this.data as any))
    //   .attr("d", d => d == null ? null : "M" + d.join("L") + "Z");

  }

}
