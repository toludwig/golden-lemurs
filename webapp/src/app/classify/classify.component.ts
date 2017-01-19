import { Component, ViewChild, OnInit, Input, Output, EventEmitter } from '@angular/core';
import * as d3 from 'd3';
import { Repo } from '../repo/repo.component';
import { RepositoryService } from '../repository.service';

function pieChart(values: number[], w: number, h: number, element) {

  let color = d3.scaleOrdinal(d3.schemeCategory10);     //builtin range of colors

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

  context.globalAlpha = 0.5;
  arcs.forEach(function(d, i) {
    context.beginPath();
    arc(d as any);
    context.fillStyle = colors('' + (i + 1));
    context.fill();
  });

  context.globalAlpha = 1;
  context.beginPath();
  arcs.forEach(arc as any);
  context.lineWidth = 1.5;
  context.stroke();
}

@Component({
  selector: 'app-classify',
  templateUrl: './classify.component.html',
  styleUrls: ['./classify.component.css']
})
export class ClassifyComponent implements OnInit {

  input = 'Enter a github repo url';
  action = 'Classify me!';
  @ViewChild('rating') rating;
  @Input() repo: string = 'https://github.com/InformatiCup/InformatiCup2017';
  @Output() fetching = false;
  @Output() result = new EventEmitter<Repo>();
  regex = /^https?:\/\/github.com\/(.+)\/(.+)$/;
  api = (name, title) => `http://localhost:8081/rate/${name}/${title}/`;
  constructor(private repositories: RepositoryService) { }

  ngOnInit() {
  }

  public classify() {
    let [name, title] = this.regex.exec(this.repo).slice(1);
    console.log(`testing: ${this.api(name, title)}`);
    this.fetching = true;
    d3.json(this.api(name, title), (response: Repo) => {
      this.fetching = false;
      this.repositories.save(`https://github.com/${name}/${title}`, response);
      pieChart(response.Rating, 100, 100, this.rating.nativeElement);
      this.result.emit(response);
    });
  }
  public repoValid(): boolean {
    return this.repo.match(this.regex) != null;
  }

}
