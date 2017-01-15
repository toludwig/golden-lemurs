import { Component, AfterViewInit, ViewChild, Input, Output, EventEmitter } from '@angular/core';
import * as d3 from 'd3';

interface Repo {
  NumberOfContributors: number;
  NumberOfIssues: number;
  Branches: number;
  Forks: number;
  Stars: number;
  Pulls: number;
  Subscribers: number;
  NumberOfCommits: number;
  User: string;
  Title: string;
  Readme: string;
  CommitMessages: string[];
  Times: [string, string];
  CommitTimes: string[];
  Files: string[];
  Category: string;
}

@Component({
  selector: 'app-data',
  templateUrl: './data.component.html',
  styleUrls: ['./data.component.css']
})
export class DataComponent implements AfterViewInit {

  @ViewChild('plot') plot;
  @ViewChild('data') datapoints;

  public categories = ["NumberOfContributors", "NumberOfIssues", "Branches", "Forks", "Stars", "Pulls", "Subscribers", "NumberOfCommits", "Category"];
  public categoryLabels = ["Contributors", "Issues", "Branches", "Forks", "Stars", "Pulls", "Subscribers", "Commits", "Category"];

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
  @Output() normalXScale: d3.ScaleLinear<number, number>;
  @Output() normalYScale: d3.ScaleLinear<number, number>;

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
        .range([this.size, this.size - this.height]);
  }

  ngAfterViewInit() {
    d3.json('assets/data.json', (error, data) => {
      if (error) {
        throw new Error("Something went wrong" + error);
      }
      this.data = data as Repo[];
      // FIXME
      for (let d of this.data) {
        d.Category = '' + Math.floor(Math.random() * 6 + 1);
      }

      this.resetScale();

      this.dataLoaded = true;
      this.repo.emit(this.data[0]);
      this.draw();
    });
  }

  draw() {
    if (!this.dataLoaded) return;
    const plot = d3.select(this.plot.nativeElement);
    const datapoints = d3.select(this.datapoints.nativeElement);

    const xDomain = [this.xStart, this.xEnd];
    const yDomain = [this.yStart, this.yEnd];

    const xScale = d3.scaleLinear()
      .domain(xDomain)
      .range([this.size, this.width - this.size]);

    const yScale = d3.scaleLinear()
      .domain(yDomain)
      .range([this.size, this.height - this.size]);

    let xValues = xScale.ticks();
    if (xValues.length == 0) xValues = [xDomain[0]];

    let yValues = yScale.ticks();
    if (yValues.length == 0) yValues = [yDomain[0]];

    const xLabel = plot.selectAll('text.xLabel').data(xValues);
    xLabel.exit().remove();
    xLabel.enter()
      .append('text').classed('xLabel', true)
      .merge(xLabel)
      .text(d => d)
      .attr('x', (d, i) => (i + 1) / xValues.length * this.width)
      .attr('y', this.height - 10)
      .attr('font-size', 10)
      .attr('text-align', 'start');

    const yLabel = plot.selectAll('text.yLabel').data(yValues);
    yLabel.exit().remove();
    yLabel.enter()
      .append('text').classed('yLabel', true)
      .merge(yLabel)
      .text(d => d)
      .attr('y', (d, i) => (9 - i) / yValues.length * this.height)
      .attr('x', 0)
      .attr('font-size', 10)
      .attr('text-align', 'start');

    const self = this;
    const zoomed = function() {
      const tr = d3.zoomTransform(this);
      datapoints.attr('transform', tr.toString());
      let screenStart = tr.invert([0, 0]);
      let screenEnd = tr.invert([self.width, self.height]);
      let domainStart = [self.normalXScale.invert(screenStart[0]), self.normalYScale.invert(screenStart[1])];
      let domainEnd = [self.normalXScale.invert(screenEnd[0]), self.normalYScale.invert(screenEnd[1])];
      console.log(`screen: ${screenStart} - ${screenEnd}`);
      console.log(`domain: ${domainStart} - ${domainEnd}`);
      [self.xStart, self.yStart] = domainStart;
      [self.xEnd, self.yEnd] = domainEnd;
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
        if (repo == null)
          throw new Error("repo is null");
        console.dir(repo);
        this.repo.emit(repo);
      });
    enter.append('circle');
    repos.merge(enter)
      .select('circle')
      .attr('cx', d => xScale(d[this.xAxis]))
      .attr('cy', d => yScale(d[this.yAxis]))
      .attr('r', () => this.size)
      .attr('fill', (d: Repo) => this.colors(d.Category));


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
