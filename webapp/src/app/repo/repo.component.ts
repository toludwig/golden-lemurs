import { Component, OnInit, Input, EventEmitter } from '@angular/core';

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

    @Input() repo: EventEmitter<Repo>;

  constructor() { }

  ngOnInit() {
  }

}
