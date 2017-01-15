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

  public categories = ["NumberOfContributors", "NumberOfIssues", "Branches", "Forks", "Stars", "Pulls", "Subscribers", "NumberOfCommits", "Category"];
  public categoryLabels = ["Contributors", "Issues", "Branches", "Forks", "Stars", "Pulls", "Subscribers", "Commits", "Category"];

  @Input() xAxis: string = 'Stars';
  @Input() yAxis: string = 'Branches';

  @Output() dataLoaded = false;
  @Output() width = 800;
  @Output() height = 600;

  @Output() repo = new EventEmitter<Repo>();

  size = 20;

  private data: Repo[];

  constructor() { }

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
      this.dataLoaded = true;
      this.repo.emit(this.data[0]);
      this.draw();
    });
  }

  draw() {
    if (!this.dataLoaded) return;
    const elem = this.plot.nativeElement;
    const plot = d3.select(elem);

    const data = attr => this.data.map(d => d[attr]);
    const domain = data => [Math.min(...data), Math.max(...data)];
    const xData = data(this.xAxis);
    const yData = data(this.yAxis);
    const xDomain = domain(xData);
    const yDomain = domain(yData);

    const xScale = d3.scaleLinear()
      .domain(xDomain)
      .range([this.size, this.width - this.size]);

    const yScale = d3.scaleLinear()
      .domain(yDomain)
      .range([this.height - this.size, this.size]);

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
      .attr('y', (d, i) => (9 - i) / 10 * this.height)
      .attr('x', 0)
      .attr('font-size', 10)
      .attr('text-align', 'start');

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const repos = plot.selectAll('g.repo').data(this.data);

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
      .attr('fill', (d: Repo) => color(d.Category));


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
