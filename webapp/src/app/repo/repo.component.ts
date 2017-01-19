import { Component, OnInit, Input, EventEmitter, Output } from '@angular/core';
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
}

@Component({
  selector: 'app-repo',
  templateUrl: './repo.component.html',
  styleUrls: ['./repo.component.css']
})
export class RepoComponent implements OnInit {

  @Output() colors = d3.scaleOrdinal(d3.schemeCategory10);
  @Input() repo: EventEmitter<Repo>;

  markdown = new MarkdownIt();

  constructor() { }

  public md2html(md: string): string {
      if (md != null)
          return this.markdown.render(md);
      else
          return '';
  }

  ngOnInit() {
  }

}
