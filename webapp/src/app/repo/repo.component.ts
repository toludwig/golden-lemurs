import { Component, OnInit, Input, EventEmitter, Output, ViewChild } from '@angular/core';
import * as d3 from 'd3';
import * as MarkdownIt from 'markdown-it';

export interface Repo {
  NumberOfContributors: number;
  //NumberOfIssues: number;
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
  Rating: number[];
}


function pieChart(values: number[], w: number, h: number, element, selected) {

  let canvas = d3.select(element).append('canvas').node() as HTMLCanvasElement;
  let context = canvas.getContext('2d');

  canvas.width = w;
  canvas.height = h;
  let radius = Math.min(w, h) / 2;

  let colors = d3.scaleOrdinal(d3.schemeCategory10);

  var arc = d3.arc()
    .outerRadius(radius - 10)
    .innerRadius(radius - 30)
    .padAngle(0.1)
    .context(context);

  var pie = d3.pie();

  var arcs = pie(values);

  context.translate(w / 2, h / 2);

  arcs.forEach(function(d, i) {
    if (i == selected)
      context.globalAlpha = 1;
    else
      context.globalAlpha = 0.3;
    context.beginPath();
    arc(d as any);
    context.fillStyle = colors('' + i);
    context.fill();
  });

  context.globalAlpha = 1;
  context.beginPath();
  arcs.forEach(arc as any);
  context.lineWidth = 1.5;
  context.stroke();
}

@Component({
  selector: 'app-repo',
  templateUrl: './repo.component.html',
  styleUrls: ['./repo.component.css']
})
export class RepoComponent implements OnInit {

  @Output() colors = d3.scaleOrdinal(d3.schemeCategory10);
  @Input() repo: EventEmitter<Repo>;
  @ViewChild('rating') rating;

  markdown = new MarkdownIt();

  constructor() { }

  public md2html(md: string): string {
    if (md != null)
      return this.markdown.render(md);
    else
      return '';
  }

  ngOnInit() {
    this.repo.subscribe((repo) => {
      let elem = this.rating.nativeElement;
      while (elem.firstChild) elem.removeChild(elem.firstChild);
      if (repo.Rating != null) {
        pieChart(repo.Rating, 100, 100, this.rating.nativeElement, +repo.Category - 1);
      }
    });
  }

}
